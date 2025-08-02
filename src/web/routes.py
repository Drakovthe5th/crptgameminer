from flask import request, jsonify, render_template
from database.firebase import get_user_balance, update_balance, get_user_data, db, SERVER_TIMESTAMP
from src.utils.security import validate_telegram_hash
from src.utils.conversions import to_xno
import datetime
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)

def configure_routes(app):
    @app.route('/')
    def index():
        return "CryptoGameBot mofo!"
    
    @app.route('/miniapp')
    def miniapp_route():
        return render_template('miniapp.html')
    
    # Telegram MiniApp API endpoints
    @app.route('/miniapp/balance', methods=['POST'])
    def miniapp_balance():
        try:
            # Get request data
            raw_data = request.get_data(as_text=True)
            init_data = request.headers.get('X-Telegram-InitData')
            
            # Validate Telegram MiniApp hash
            if not validate_telegram_hash(init_data, raw_data, app.config['TELEGRAM_TOKEN']):
                return jsonify({'success': False, 'error': 'Invalid hash'}), 401
            
            # Extract user ID from initData
            user_id = extract_user_id(init_data)
            if not user_id:
                return jsonify({'success': False, 'error': 'User ID not found'}), 400
            
            # Get user balance
            balance = get_user_balance(user_id)
            return jsonify({
                'success': True,
                'balance': to_xno(balance),
                'min_withdrawal': app.config['MIN_WITHDRAWAL']
            })
        except Exception as e:
            logger.error(f"MiniApp balance error: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/miniapp/play', methods=['POST'])
    def miniapp_play_game():
        try:
            # Validate request
            init_data = request.headers.get('X-Telegram-InitData')
            raw_data = request.get_data(as_text=True)
            
            if not validate_telegram_hash(init_data, raw_data, app.config['TELEGRAM_TOKEN']):
                return jsonify({'success': False, 'error': 'Invalid hash'}), 401
            
            # Extract user ID
            user_id = extract_user_id(init_data)
            if not user_id:
                return jsonify({'success': False, 'error': 'User ID not found'}), 400
            
            # Process game request
            data = request.get_json()
            game_type = data.get('game_type')
            
            # Get user data
            user_data = get_user_data(user_id)
            now = datetime.datetime.now()
            
            # Check cooldown
            last_played = user_data.get('last_played', {}).get(game_type)
            if last_played and (now - last_played).seconds < 300:  # 5 min cooldown
                cooldown = 300 - (now - last_played).seconds
                return jsonify({
                    'success': False,
                    'error': f'Please wait {cooldown} seconds before playing again'
                })
            
            # Calculate reward (simplified for example)
            rewards = {
                'trivia': 0.01,
                'clicker': 0.015,
                'spin': 0.02
            }
            reward = rewards.get(game_type, 0.01)
            
            # Update balance
            new_balance = update_balance(user_id, reward)
            
            # Update last played time
            update_data = {f'last_played.{game_type}': now}
            db.collection('users').document(str(user_id)).update(update_data)
            
            return jsonify({
                'success': True,
                'reward': reward,
                'new_balance': to_xno(new_balance)
            })
        except Exception as e:
            logger.error(f"MiniApp play error: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/miniapp/withdraw', methods=['POST'])
    def miniapp_withdraw():
        try:
            # Validate request
            init_data = request.headers.get('X-Telegram-InitData')
            raw_data = request.get_data(as_text=True)
            
            if not validate_telegram_hash(init_data, raw_data, app.config['TELEGRAM_TOKEN']):
                return jsonify({'success': False, 'error': 'Invalid hash'}), 401
            
            # Extract user ID
            user_id = extract_user_id(init_data)
            if not user_id:
                return jsonify({'success': False, 'error': 'User ID not found'}), 400
            
            # Process withdrawal
            data = request.get_json()
            method = data.get('method')
            details = data.get('details')
            
            # Get user balance
            balance = get_user_balance(user_id)
            
            # Check minimum withdrawal
            if balance < app.config['MIN_WITHDRAWAL']:
                return jsonify({
                    'success': False,
                    'error': f'Minimum withdrawal: {app.config["MIN_WITHDRAWAL"]} XNO'
                })
            
            # Process withdrawal (simplified)
            # In a real implementation, you'd call your withdrawal processor
            tx_id = f"TX-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Record withdrawal
            withdrawal_data = {
                'user_id': user_id,
                'method': method,
                'amount': balance,
                'details': details,
                'status': 'pending',
                'tx_id': tx_id,
                'timestamp': SERVER_TIMESTAMP
            }
            db.collection('withdrawals').add(withdrawal_data)
            
            # Reset balance
            update_balance(user_id, -balance)
            
            return jsonify({
                'success': True,
                'message': f'Withdrawal of {to_xno(balance):.6f} XNO is processing!'
            })
        except Exception as e:
            logger.error(f"MiniApp withdrawal error: {str(e)}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    # GitHub webhook for auto-deployment
    @app.route('/webhooks/github', methods=['POST'])
    def github_webhook():
        try:
            # Get GitHub signature
            signature = request.headers.get('X-Hub-Signature', '')
            secret = app.config.get('GITHUB_WEBHOOK_SECRET')
            
            # Verify signature
            if secret and not verify_github_signature(signature, request.data, secret):
                return jsonify({'error': 'Invalid signature'}), 401
            
            # Check if it's a push to main branch
            payload = request.get_json()
            if payload.get('ref') == 'refs/heads/main':
                # In a real implementation, this would trigger a deployment
                # For Cloud Run, we'd redeploy the service
                logger.info("GitHub webhook received - deployment should be triggered")
                return jsonify({'status': 'deployment triggered'})
            
            return jsonify({'status': 'ignored'})
        except Exception as e:
            logger.error(f"GitHub webhook error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
        
    @app.route('/webhook', methods=['POST'])
    def telegram_webhook():
        from telegram import Update
        from src.main import application  # Import after initialization
        
        # Verification
        token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if token != app.config['TELEGRAM_TOKEN']:
            return 'Unauthorized', 401
        
        # Process update
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
        return 'ok', 200

# Helper functions
def extract_user_id(init_data):
    """Extract user ID from Telegram initData"""
    try:
        import urllib.parse
        data_dict = urllib.parse.parse_qs(init_data)
        user_str = data_dict.get('user', [''])[0]
        if user_str:
            user_data = json.loads(user_str)
            return user_data.get('id')
    except Exception as e:
        logger.error(f"Error extracting user ID: {str(e)}")
    return None

def verify_github_signature(signature, payload, secret):
    """Verify GitHub webhook signature"""
    try:
        digest = hmac.new(secret.encode(), payload, hashlib.sha1).hexdigest()
        expected = f'sha1={digest}'
        return hmac.compare_digest(signature, expected)
    except Exception:
        return False