import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("lesson14.csv")


print(df.info())

plt.figure(figsize=(10,6))
sns.histplot(df['Average IQ'])

plt.show()