import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("lesson14.csv")

plt.figure(figsize=(10,6))

plt.scatter(
    data["Mean years of schooling - 2021"],
    data["Average IQ"],
    color="purple",
    alpha=0.7
)

plt.show()