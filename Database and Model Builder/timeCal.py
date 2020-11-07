from datetime import timedelta
from settings import SAMPLE_SIZE, ESTIMATED_CROLL_TIME, ESTIMATED_MATCHLIST_TIME, AVERAGE_MATCH_COUNT, DELAY

step1 = ESTIMATED_CROLL_TIME * SAMPLE_SIZE
step2 = ESTIMATED_MATCHLIST_TIME * SAMPLE_SIZE
step3 = AVERAGE_MATCH_COUNT * DELAY * SAMPLE_SIZE

def printCrollTime():
    print('Estimated Time:', timedelta(seconds=step1))

def printMatchlistTime():
    print('Estimated Time:', timedelta(seconds=step2))

def printMatchTime():
    print('Estimated Time:', timedelta(seconds=step3))

if __name__ == "__main__":
    print('Estimated Time:', timedelta(seconds=step1 + step2 + step3))