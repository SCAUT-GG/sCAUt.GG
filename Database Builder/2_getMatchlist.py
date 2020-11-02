import requests
from time import sleep
from datetime import datetime
from pymongo import MongoClient
from settings import ADDRESS, PORT, DATABASE_NAME, LEVEL, SAMPLE_SIZE, DELAY, API_KEY
from timeCal import printMatchlistTime

def timestampToDatetime(timestamp):
    return datetime.fromtimestamp(timestamp//1000)

ACCOUNT_ID_URL = 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/{}?api_key={}'
MATCHLIST_URL = 'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?queue=420&endTime={}&beginTime={}&api_key={}'
WEEK_IN_MILLISEC = 3600 * 24 * 7 * 1000

client = MongoClient(ADDRESS, PORT)
db = client[DATABASE_NAME]

summoners =  list(db['{}_{}_summoners'.format(LEVEL, SAMPLE_SIZE)].find({}))

count = 0
succesCount = 0
fails = []
start = datetime.now()
printMatchlistTime()
for summoner in summoners:
    count += 1
    try:
        acc_res = requests.get(ACCOUNT_ID_URL.format(summoner['summonerId'], API_KEY))
        sleep(DELAY)
        acc_entry = acc_res.json()
        
        if acc_res.status_code != 200 or acc_entry == None:
            raise Exception('AccountId', acc_res.status_code, acc_entry)

        diff = (summoner['end'][1] - summoner['begin'][1]) // WEEK_IN_MILLISEC + 1
        begin = summoner['begin'][1]
        end = (summoner['begin'][1] + WEEK_IN_MILLISEC) if diff > 1 else summoner['end'][1]
        # print(acc_entry['accountId'])
        matches = []
        for _ in range(diff):
            try:
                ml_res = requests.get(MATCHLIST_URL.format(acc_entry['accountId'], end, begin, API_KEY))
                sleep(DELAY)
                ml_entry = ml_res.json()
                
                if ml_res.status_code != 200 or ml_entry == None:
                    raise Exception('Matchlist', ml_res.status_code, ml_entry)

                matches += ml_entry['matches']
            except Exception as e:
                # print('Page', e)
                pass


            # print('begin', timestampToDatetime(begin))
            # print('end  ', timestampToDatetime(end))
            # print('Match', len(matches))
            begin = end + 1
            end = end + WEEK_IN_MILLISEC if end + WEEK_IN_MILLISEC < summoner['end'][1] else summoner['end'][1]

        q = {'_id': summoner['_id']}
        v = {
            'accountId': acc_entry['accountId'],
            'matches': matches
            }
        db['{}_{}_summoners'.format(LEVEL, SAMPLE_SIZE)].update_one(q, {'$set': v})
        succesCount += 1
    except Exception as e:
        print(e)
        fails.append(summoner['summonerId'])
    print(count, succesCount, SAMPLE_SIZE, datetime.now() - start)

print(fails)



