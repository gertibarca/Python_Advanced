from matplotlib import pyplot as plt
import pandas as pd


df = pd.read_csv("lesson14.csv")


nobel_prizes = df.groupby("Continent")["Nobel Prices"].sum()


colors = [
    "gold",
    "lightcoral",
    "yellow",
    "orange",
    "lightskyblue",
    "aquamarine",
    "burlywood"
]

plt.figure(figsize=(10, 10))

nobel_prizes.plot(
    kind="pie",
    colors=colors,
    autopct="%1.1f%%"
)

plt.title("Nobel Prizes by Continent")
plt.ylabel("")
plt.show()