from glob import glob
import pandas as pd
import yaml
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns

###
from scipy import linalg

from sklearn.decomposition import PCA
# %%

def data_into_dict(data):
    res = {}
    for e in data:
        key = e["type"][0][:-1]
        value = e["value"]
        res[key] = value
    return res

data = []
for filename in glob(r"C:\Users\Surface\Downloads\gamithra_mood-master\*00"):
    with open(filename, 'r') as f:
        line = yaml.load(f)
        time = datetime.strptime(line["date"] + " " + line["time"], "%d.%m.%Y %H:%M")
        dat = data_into_dict(line["data"])
        data.append({"time": time, **dat})
        # print(time, data, line["data"])

df = pd.DataFrame.from_records(data, exclude=["anxiety", "chaos", "depression", "melancholy"])

# %%
df.set_index("time")
df.sort_index(inplace=True)
df.to_csv("gamitra.csv")
# %%
df['date_delta'] = (df['time'] - df['time'].min())  / np.timedelta64(1,'D')

# %%
features = ['health', 'self-worth', 'gratitude', 'generosity', 'belonging',
       'future', 'present', 'past', 'gratification', 'focus', 'independence',
            'wellbeing']
for key in features:
    sns.lmplot(x='date_delta', y=key, data=df )
    #plt.show()
    plt.savefig(key + ".png", dpi=180, pad_inches=1, bbox_inches="tight")
# %%

#corr_mat = df[features].corr().stack().reset_index(name="correlation")
corr = df[features].corr()
sns.heatmap(corr, annot=True, fmt=".1f")
# plt.show()
plt.savefig("correlations.png",dpi=180, pad_inches=1, bbox_inches="tight")

# %%
X = df[features] / 10
pca = PCA(n_components=2)
X_transformed = pca.fit_transform(X)
# %%
# tdf = pd.DataFrame(X_transformed)
# tdf.columns = ["x", "y"]
# sns.scatterplot(x="x", y="y", data=tdf)
# plt.show()
# %%
print("### PCA")
print("explained variance", pca.explained_variance_ratio_)
comps = zip(X.columns, pca.components_[1])
sorted_comps = dict(sorted(comps, key=lambda x: abs(x[1])))
print("components", sorted_comps)

