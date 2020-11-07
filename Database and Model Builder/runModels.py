from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, Lasso, LinearRegression, ElasticNet
from sklearn.neighbors import KNeighborsRegressor

from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler

import numpy as np
import pandas as pd
import pickle

from pymongo import MongoClient

from settings import ADDRESS, PORT, DATABASE_NAME, LEVEL, SAMPLE_SIZE

LEVEL = 16
SAMPLE_SIZE = 500

model_dict = {
    'RandomForestRegressor': RandomForestRegressor(),
    'SVR': SVR(),
    'Ridge': Ridge(),
    'Lasso': Lasso(),
    'LinearRegression': LinearRegression(),
    'ElasticNet': ElasticNet(),
    'KNeighborsRegressor': KNeighborsRegressor(),
}


client = MongoClient(ADDRESS, PORT)
db = client[DATABASE_NAME]

df = pd.DataFrame(db['{}_{}_datas'.format(LEVEL, SAMPLE_SIZE)].find())

testDf = df.sample(n=SAMPLE_SIZE//5)
trainDf = df[~df.accountId.isin(testDf.accountId)]

# trainDf = pd.DataFrame(db['{}_{}_datas'.format(LEVEL, SAMPLE_SIZE)].find())
# testDf = pd.DataFrame(db['{}_{}_datas'.format(LEVEL, 50 )].find())

for modelName, model in model_dict.items():
    infos = ['_id', 'accountId']

    x_cols = df.drop(['_id', 'accountId', 'promotion'], axis=1).columns.tolist()
    y_cols = ['promotion']

    x_train = trainDf[x_cols]
    y_train = trainDf[y_cols]

    x_test = testDf[x_cols]
    y_test = testDf[y_cols]

    model.fit(x_train, y_train.values.ravel())
    fileName = modelName + '.sav'
    pickle.dump(model, open(fileName, 'wb'))
    y_predict = model.predict(x_test) >= 0.5

    # print(modelName, 'mse: ', mean_squared_error(y_test, y_predict))
    # print(modelName, 'r2 :', r2_score(y_test, y_predict))

    print(modelName, 'mse: ', mean_squared_error(list(map(lambda x: 1 if x else 0, y_test.promotion.values)), list(map(lambda x: 0 if x else 1, y_predict))))
    print(modelName, 'r2 :', r2_score(y_test, y_predict))


    # print(list(map(lambda x: 1 if x else 0, y_test.promotion.values)))
    # print(list(map(lambda x: 0 if x else 1, y_predict)))
    count = sum([y_predict[i] == y_test.promotion.values[i] for i in range(len(y_predict))])
    print('{}/{} => {}%'.format(count, len(y_predict), 100*count/len(y_predict)))