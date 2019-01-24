from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
import sys

def formatter(y, pos):
    return 'P' + str(int(y))

f = sys.argv[1]
df = pd.read_csv(f)
# df.amin = pd.to_datetime(df.amin).astype(datetime)
# df.amax = pd.to_datetime(df.amax).astype(datetime)

ax = plt.figure().gca()
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(formatter))
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

ys = max(df.pid)
plt.ylim(-.9,ys+.9)

# ax = ax.xaxis_date()
ax.hlines(df.pid, df.start, df.start + df.duration, lw=20)
for index, row in df.iterrows():
	plt.text(row['start']+(row['duration']/2), row['pid'], 'T'+str(row['tid']), color='w', ha='center', va='center')
ax.plot(df.start, df.pid, '|', ms=25, mew=2, color='gray')
ax.plot(df.start + df.duration, df.pid, '|', ms=25, mew=2, color='gray')
# print(df)
plt.xlabel('tempo')
plt.ylabel('processador')
plt.show()
