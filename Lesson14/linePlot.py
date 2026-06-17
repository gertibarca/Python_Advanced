from matplotlib import pyplot as plt
import pandas as pd

data = pd.read_csv("lesson14.csv")

avg_iq_by_continent= data.groupby("Continent")["Average IQ"].mean()
plt.figure(figsize=(10,6))

avg_iq_by_continent.plot(kind="line",marker="o")

plt.show()