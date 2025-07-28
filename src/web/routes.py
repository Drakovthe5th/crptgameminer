from flask import request, jsonify, render_template
from src.database.firebase import get_user_balance, get_user_data, update_balance, db
from src.features.quests import get_active_quests, complete_quest
from src.utils.security import validate_telegram_hash
from src.utils.conversions import to_xno, usd_to_xno
from config import Config
import logging
import datetime

logger = logging.getLogger(__name__)

def configure_routes(app):
    @app.route('/')
    def index():
        return "CryptoGameBot is running!"
    
    @app.route('/miniapp')
    def miniapp_route():
        return render_template('miniapp.html')
    
    # MiniApp API routes
    @app.route('/miniapp/balance', methods=['POST'])
    def miniapp_balance():
        try:
            # Validate Telegram hash
            init_data = request.headers.get('X-Telegram-Hash')
            user_id = request.headers.get('X-Telegram-User')
            raw_data = request.get_data(as_text=True)
            
            if not validate_telegram_hash(init_data, raw_data):
                return jsonify({'success': False, 'error': 'Invalid hash'}), 401
            
            balance = get_user_balance(int(user_id))
            return jsonify({'success': True, 'balance': to_xno(balance)})
        except Exception as e:
            logger.error(f"MiniApp balance error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/miniapp/play', methods=['POST'])
    def miniapp_play_game():
        try:
            data = request.get_json()
            user_id = int(data['user_id'])
            game_type = data['game_type']
            
            # Check cooldown
            user_data = get_user_data(user_id)
            now = datetime.datetime.now()
            last_played = user_data.get('last_played', {}).get(game_type)
            
            if last_played and (now - last_played).seconds < Config.GAME_COOLDOWN * 60:
                cooldown = Config.GAME_COOLDOWN * 60 - (now - last_played).seconds
                return jsonify({
                    'success': False,
                    'error': f'Please wait {cooldown // 60} minutes before playing again'
                })
            
            # Process game play and award rewards
            reward_key = f"{game_type}_reward"
            reward = Config.REWARDS.get(reward_key, 0.01)
            new_balance = update_balance(user_id, reward)
            
            # Update last played time
            update_user(user_id, {f'last_played.{game_type}': now})
            
            # Update leaderboard points
            points = 5 if game_type == 'trivia' else 1
            update_leaderboard_points(user_id, points)
            
            return jsonify({
                'success': True,
                'reward': reward,
                'new_balance': new_balance
            })
        except Exception as e:
            logger.error(f"MiniApp play error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/miniapp/withdraw', methods=['POST'])
    def miniapp_withdraw():
        try:
            data = request.get_json()
            user_id = int(data['user_id'])
            method = data['method']
            details = data['details']
            
            # Get user balance
            balance = get_user_balance(user_id)
            
            if balance < Config.MIN_WITHDRAWAL:
                return jsonify({
                    'success': False,
                    'error': f'Minimum withdrawal: {Config.MIN_WITHDRAWAL} XNO'
                })
            
            # Process withdrawal
            result = process_withdrawal(user_id, method, balance, details)
            
            if result.get('status') == 'success':
                update_balance(user_id, -balance)
                return jsonify({
                    'success': True,
                    'message': f'Withdrawal of {balance:.6f} XNO is processing!'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Withdrawal failed')
                })
                
        except Exception as e:
            logger.error(f"MiniApp withdrawal error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # PayPal webhook handler
    @app.route('/paypal/webhook', methods=['POST'])
    def paypal_webhook():
        try:
            # Verify webhook signature
            if not verify_paypal_webhook(request.headers, request.data):
                return jsonify({'status': 'invalid signature'}), 401
                
            event = request.json
            event_type = event.get('event_type')
            
            if event_type == 'PAYMENT.PAYOUTS-ITEM.SUCCEEDED':
                # Handle successful payout
                payout_item = event['resource']
                payout_batch_id = payout_item['payout_batch_id']
                
                # Update withdrawal status in database
                withdrawal_ref = db.collection('withdrawals')
                query = withdrawal_ref.where('result.tx_id', '==', payout_batch_id).limit(1).stream()
                
                for doc in query:
                    doc.reference.update({'status': 'completed'})
                    # Record successful transaction
                    db.collection('transactions').add({
                        'type': 'withdrawal_completed',
                        'withdrawal_id': doc.id,
                        'timestamp': SERVER_TIMESTAMP
                    })
                
            elif event_type == 'PAYMENT.PAYOUTS-ITEM.FAILED':
                # Handle failed payout
                payout_item = event['resource']
                payout_batch_id = payout_item['payout_batch_id']
                reason = payout_item.get('errors', {}).get('reason', 'Unknown error')
                
                # Update withdrawal status in database
                withdrawal_ref = db.collection('withdrawals')
                query = withdrawal_ref.where('result.tx_id', '==', payout_batch_id).limit(1).stream()
                
                for doc in query:
                    doc.reference.update({
                        'status': 'failed',
                        'result.error': reason
                    })
                
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            logger.error(f"PayPal webhook error: {str(e)}")
            return jsonify({'status': 'error'}), 500
        
    # M-Pesa callback handler (fixed indentation)
    @app.route('/mpesa-callback', methods=['POST'])
    def mpesa_callback():
        """
        Handle M-Pesa payment callback
        Sample payload:
        {
            "Result": {
                "ResultType": 0,
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "OriginatorConversationID": "10571-13142494-1",
                "ConversationID": "AG_20240512_00006f9e6c7b4c1d97c9",
                "TransactionID": "LGR0000000",
                "ResultParameters": {
                    "ResultParameter": [
                        {"Key": "TransactionAmount", "Value": 10},
                        {"Key": "TransactionReceipt", "Value": "LGR0000000"},
                        {"Key": "ReceiverPartyPublicName", "Value": "600978 - Safaricom"},
                        {"Key": "TransactionCompletedDateTime", "Value": "20240512000000"},
                        {"Key": "ReceiverParty", "Value": "600978"}
                    ]
                }
            }
        }
        """
        try:
            data = request.json
            logger.info(f"M-Pesa callback received: {data}")
            
            # Validate transaction
            if data.get('Result', {}).get('ResultCode') == 0:
                # Successful transaction
                params = {item['Key']: item['Value'] for item in 
                         data['Result']['ResultParameters']['ResultParameter']}
                
                logger.info(f"Successful M-Pesa transaction: {params}")
                return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})
            else:
                # Failed transaction
                error_desc = data.get('Result', {}).get('ResultDesc', 'Unknown error')
                logger.error(f"M-Pesa transaction failed: {error_desc}")
                return jsonify({"ResultCode": 1, "ResultDesc": "Failed"}), 400
                
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {str(e)}")
            return jsonify({"ResultCode": 1, "ResultDesc": "Server error"}), 500