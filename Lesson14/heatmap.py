import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("lesson14.csv")

df["Population - 2023"] = df["Population - 2023"].str.replace(",","").astype(float)

numeric_iq_data_loc = df.select_dtypes(include=["number"])

sns.heatmap(numeric_iq_data_loc.corr(), annot=True,cmap="coolwarm",fmt=".2f")

plt.tight_layout()
plt.show()