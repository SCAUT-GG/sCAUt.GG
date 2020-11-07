_TIERS = (
    'IRON','BRONZE', 'SILVER',
    'GOLD', 'PLATINUM', 'DIAMOND',
    'MASTER', 'GRANDMASTER', 'CHALLENGER'
    )
_RANKS = ('IV', 'III', 'II', 'I')

def integer_to_tier_rank(i):
    if i > 24:
        return _TIERS[6 + i - 25], _RANKS[3]
    else:
        return _TIERS[(i-1)//4], _RANKS[(i-1)%4]

integer_to_tier_rank(24)

ADDRESS = 'localhost'
PORT = 27017
DATABASE_NAME = 'lol_database'

LEVEL = 16
PROMOTE = LEVEL + 1
DEMOTE =  LEVEL - 1
TIER, RANK = integer_to_tier_rank(LEVEL)

API_KEY = 'RGAPI-d72f7157-cd59-44fa-9704-7f0a4c20946b'
SAMPLE_SIZE = 250 * 2
DELAY = 1.1

ESTIMATED_CROLL_TIME = 12.78
ESTIMATED_MATCHLIST_TIME = 8.4
AVERAGE_MATCH_COUNT = 35