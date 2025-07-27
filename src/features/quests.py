from src.database.firebase import quests_ref, update_balance, update_leaderboard_points
from config import Config

def get_active_quests():
    return quests_ref.where('active', '==', True).stream()

def complete_quest(user_id: int, quest_id: str):
    quest_doc = quests_ref.document(quest_id).get()
    if not quest_doc.exists:
        return False
        
    quest_data = quest_doc.to_dict()
    reward_xno = quest_data.get('reward_xno', 0)
    reward_points = quest_data.get('reward_points', 0)
    
    # Award rewards
    update_balance(user_id, reward_xno)
    update_leaderboard_points(user_id, reward_points)
    
    # Record completion
    quests_ref.document(quest_id).update({
        'completions': firestore.Increment(1)
    })
    
    user_ref = get_user_ref(user_id)
    user_ref.update({
        f'completed_quests.{quest_id}': SERVER_TIMESTAMP
    })
    
    return True