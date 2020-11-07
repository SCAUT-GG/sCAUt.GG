import numpy as np
import pandas as pd
from pymongo import MongoClient
from collections import defaultdict

from settings import ADDRESS, PORT, DATABASE_NAME, LEVEL, SAMPLE_SIZE

# LEVEL = 16 #**************
# SAMPLE_SIZE = 50 #*******

FEATURES = ('kills', 'deaths', 'assists', 'largestKillingSpree', 'largestMultiKill', 'killingSprees', 'totalDamageDealt', 'totalDamageDealtToChampions', 'totalDamageTaken', 'goldEarned', 'goldSpent', 'totalMinionsKilled', 'totalTimeCrowdControlDealt', 'champLevel')

def getRatio(a, b):
    if a + b == 0:
        return 0
    else:
        return a / (a + b)

client = MongoClient(ADDRESS, PORT)
db = client[DATABASE_NAME]

newCollection = db['{}_{}_datas'.format(LEVEL, SAMPLE_SIZE)]
# newCollection = db['sample_{}_{}_datas'.format(LEVEL, SAMPLE_SIZE)]

stats = []

for s in db['{}_{}_summoners'.format(LEVEL, SAMPLE_SIZE)].find({}):
# for s in db['sample_{}_{}_summoners'.format(LEVEL, SAMPLE_SIZE)].find({}):
    gameIds = [match['gameId'] for match in s['matches']]
    matchResults = []
    for match in db['{}_{}_matches'.format(LEVEL, SAMPLE_SIZE)].find({'gameId': {'$in': gameIds}}):
        matchResult = {}
        participantId = 0
        for participantIdentity in match['participantIdentities']:
            if participantIdentity['player']['accountId'] == s['accountId']:
                participantId = participantIdentity['participantId']
                break

        me = match['participants'][participantId-1]
        matchResult['win'] = me['stats']['win']
        matchResult['you'] = False
        you = None
        for p in match['participants']:
            if all(
                [me['teamId'] != p['teamId'],
                me['timeline']['role'] == p['timeline']['role'],
                me['timeline']['lane'] == p['timeline']['lane']]
                ):
                matchResult['you'] = True
                you = p
                break

        for feature in FEATURES:
            if you:
                matchResult[feature] = getRatio(me['stats'][feature], you['stats'][feature])
            else:
                matchResult[feature] = 0
        
        matchResults.append(matchResult)

    matchResults = pd.DataFrame(matchResults)

    stat = pd.Series(index=['accountId', 'promotion', 'gameCount', 'win', 'loss', 'missing'] + list(FEATURES), dtype='object')
    stat['accountId'] = s['accountId']
    stat['promotion'] = s['promotion']
    stat['gameCount'] = matchResults.shape[0]
    winCount = matchResults[matchResults['win'] == True].shape[0]
    lossCount = matchResults.shape[0] - winCount
    stat['win'] = getRatio(winCount, lossCount)
    stat['loss'] = getRatio(lossCount, winCount)
    stat['missing'] = matchResults[matchResults['you'] == False].shape[0]
    stat[list(FEATURES)] = matchResults.sum()[list(FEATURES)] / (stat['gameCount'] - stat['missing'])
    stats.append(stat)

stats = pd.DataFrame(stats)
newCollection.insert_many(stats.to_dict(orient='records'))

    