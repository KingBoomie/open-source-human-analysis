from glob import glob
from datetime import datetime
from itertools import cycle

import yaml
import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set()

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
for filename in glob(r"gamithra_mood/*:00"):
    with open(filename, 'r') as f:
        line = yaml.load(f)
        time = datetime.strptime(line["date"] + " " + line["time"], "%d.%m.%Y %H:%M")
        dat = data_into_dict(line["data"])
        data.append({"time": time, **dat})
        # print(time, data, line["data"])

df = pd.DataFrame.from_records(data, exclude=["anxiety", "chaos", "depression", "melancholy"])

# %%
df['date_delta'] = (df['time'] - df['time'].min()) / np.timedelta64(1,'D')
df = df.set_index("time")
df.sort_index(inplace=True)
# df.to_csv("gamithra.csv")

# %%
os.chdir("results")
features = ['self-worth', 'future', 'past', 'belonging', 'independence', 'wellbeing', 'generosity', 'focus', 'gratitude', 'health', 'present', 'gratification']

# %%
# summarise points
colors = cycle(sns.color_palette("muted"))

fig, axs = plt.subplots(4,3, sharex="all", sharey="all", figsize=(12, 10))
for key, ax in zip(features, axs.flat):
    sns.regplot(ax=ax, x=df.index, y=key, data=df, lowess=True, color=next(colors))
    ax.set_title(key)
    # ax.set_xlabel("")
    ax.tick_params(axis='y', labelleft=True)

plt.show()
sns.despine()
# plt.savefig("summarise_points.png", dpi=180, pad_inches=1, bbox_inches="tight")


# %%
# cumulative change
colors = cycle(sns.color_palette("muted"))

fig, axs = plt.subplots(4,3, sharex="all", sharey="row", figsize=(12, 10))
for key, ax in zip(features, axs.flat):
    ax.plot((df[key] - 5).cumsum(), color=next(colors))
    ax.set_title(key)

fig.autofmt_xdate()
# plt.show()
plt.savefig("cumulative_change.png", dpi=180, pad_inches=1, bbox_inches="tight")
plt.show()
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
sorted_comps = dict(sorted(comps, key=lambda x: abs(x[1]), reverse=True))
print("components", sorted_comps)

