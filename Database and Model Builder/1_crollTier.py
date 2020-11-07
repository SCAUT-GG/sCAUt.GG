import requests, re, time, json, sys, random
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
from datetime import datetime, timedelta
from settings import ADDRESS, PORT, DATABASE_NAME, LEVEL, PROMOTE, DEMOTE, TIER, RANK, SAMPLE_SIZE
from timeCal import printCrollTime

ESTIMATED_TIME_PER_SAMPLE = 8.75
MIN_DATE = datetime(2020, 4, 1)

def isFitForCriteria(summoner, curr, prev):
    currIndex = -1
    for idx, timestamp in reversed(list(enumerate(summoner['timestamp']))):
        if timestamp[1] == curr:
            currIndex = idx
            break

    if 1 < currIndex and summoner['timestamp'][currIndex-1][1] == prev:
        if MIN_DATE <= summoner['timestamp'][currIndex-1][0]:
            summoner['begin'] = [summoner['timestamp'][currIndex-1][0] , int(summoner['timestamp'][currIndex-1][0].timestamp() * 1000)]
            summoner['end'] = [summoner['timestamp'][currIndex][0], int(summoner['timestamp'][currIndex][0].timestamp() * 1000 - 1)]
            summoner['before'] = prev
            summoner['after'] = curr
            return True

    # print(summoner['timestamp'][currIndex][1], summoner['timestamp'][currIndex-1][1])
    
    return False

def convertTimestamp(timestamp):
    return [datetime.fromtimestamp(timestamp[0]//1000), timestamp[1]]

def filterTimeStamps(timestamps):
    timestamps = [t for t in timestamps if t]
    if len(timestamps) == 0:
        return []

    result = [convertTimestamp(timestamps[0])]
    for timestamp in timestamps[1:]:
        if result[-1][1] != timestamp[1]:
            result.append(convertTimestamp(timestamp))

    return result


URL = 'https://www.leagueofgraphs.com/ko/summoner/kr/{summonerName}'

client = MongoClient(ADDRESS, PORT)
db = client[DATABASE_NAME]

summoners = list(db['ranked_solo_5x5_summoners'].find({'tier': TIER, 'rank': RANK}))
newCollection = db['{}_{}_summoners'.format(LEVEL, SAMPLE_SIZE)]
driver = webdriver.Edge('msedgedriver.exe')

count = 0
promoteTarget = SAMPLE_SIZE // 2
demoteTarget = SAMPLE_SIZE // 2
start = datetime.now()
# random.seed(0)
random.shuffle(summoners)
printCrollTime()
for s in summoners:
    try:
        driver.get(URL.format(summonerName=s['summonerName'].replace(' ', '+')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script = soup.select_one('#rankingHistory-1 > script:nth-child(3)')
        match = re.compile("data: (.*)").search(str(script))
        datas = filterTimeStamps(json.loads(match.group(1)[:-1]))
        s.update({'timestamp': datas})
        if 0 < promoteTarget and isFitForCriteria(s, PROMOTE, LEVEL):#promotion
            s.update({'promotion': True})
            newCollection.insert_one(s)
            promoteTarget -= 1
        elif 0 < demoteTarget and isFitForCriteria(s, DEMOTE, LEVEL):#demotion:
            s.update({'promotion': False})
            newCollection.insert_one(s)
            demoteTarget -= 1
    except:
        pass

    count += 1
    print(count, SAMPLE_SIZE - promoteTarget - demoteTarget, SAMPLE_SIZE, datetime.now() - start)
    if promoteTarget == 0 and demoteTarget == 0:
        break
    
driver.close()