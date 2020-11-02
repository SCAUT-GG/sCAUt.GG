import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pymongo import MongoClient

from settings import ADDRESS, PORT, DATABASE_NAME, LEVEL, SAMPLE_SIZE

client = MongoClient(ADDRESS, PORT)
db = client[DATABASE_NAME]

df = pd.DataFrame(db['{}_{}_datas'.format(LEVEL, SAMPLE_SIZE)].find())

df.gameCount.plot.hist(by='gameCount', bins=df.shape[0])

# correlations = df.corr()['promotion'].sort_values()

# plt.bar(correlations[:-1].index.astype(str)[::-1], 100*correlations[:-1][::-1],color='r')

# # Plot labeling
# plt.xticks(rotation=75) ; plt.xlabel('Correlations'); plt.ylabel('Correlation (%)');
# plt.title('Correlations with Promotion')


# high_corr = df.loc[:,list(correlations.tail(6)[::-1].index)]
# sns.pairplot(high_corr,diag_kind='kde')

# low_corr = df.loc[:,['promotion']+list(correlations.head(5).index)]
# sns.pairplot(low_corr,diag_kind='kde')

plt.show()