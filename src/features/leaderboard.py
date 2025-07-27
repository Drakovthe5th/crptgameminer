from src.database.firebase import users_ref
from src.database.firebase import update_leaderboard_points

def get_leaderboard(limit=10):
    top_users = users_ref.order_by('points', direction='DESCENDING').limit(limit).stream()
    return [user.to_dict() for user in top_users]

def get_user_rank(user_id: int):
    all_users = users_ref.order_by('points', direction='DESCENDING').stream()
    for rank, user in enumerate(all_users, start=1):
        if user.id == str(user_id):
            return rank
    return -1