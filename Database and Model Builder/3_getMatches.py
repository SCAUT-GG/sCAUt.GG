import requests
from time import sleep
from datetime import datetime, timedelta
from pymongo import MongoClient
from settings import ADDRESS, PORT, DATABASE_NAME, API_KEY, DELAY, LEVEL, SAMPLE_SIZE
from timeCal import printMatchTime

MATCH_URL = 'https://kr.api.riotgames.com/lol/match/v4/matches/{}?api_key={}'

client = MongoClient(ADDRESS, PORT)
db = client[DATABASE_NAME]

summoners = list(db['{}_{}_summoners'.format(LEVEL, SAMPLE_SIZE)].find({}))
newCollection = db['{}_{}_matches'.format(LEVEL, SAMPLE_SIZE)]

gameIds = sorted(set(m['gameId'] for s in summoners for m in s['matches']))
print(len(gameIds), len([m['gameId'] for s in summoners for m in s['matches']]))
# gameIds = [4279532982, 4597055210, 4656758622]

fails = []
successCount = 0
count = 0
gameCount = len(gameIds)
printMatchTime()
print('More Accutate Estimated Time:', timedelta(seconds=int(len(gameIds) * (DELAY + 0.1))))
start = datetime.now()
for gameId in gameIds:
    count += 1
    try:
        response = requests.get(MATCH_URL.format(gameId, API_KEY))
        sleep(DELAY)
        entry = response.json()
        
        if response.status_code != 200 or entry == None:
            raise Exception(response.status_code, entry)

        newCollection.insert_one(entry)
        successCount += 1
    except Exception as e:
        fails.append(gameId)
        # print('\n', gameId, '\n', e)
    
    print(count, successCount, gameCount, datetime.now()-start)

print(fails)
print(len(gameIds), len([m['gameId'] for s in summoners for m in s['matches']]))