import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("lesson14.csv")

filtered_df = df[df["Average IQ"]>=100]

print(filtered_df)


filtered_df = filtered_df.sort_values(by="Average IQ",ascending=False)

print(filtered_df)


plt.figure(figsize=(14,8))

bars = plt.bar(filtered_df["Country"],
               filtered_df["Average IQ"],
               color="skyblue")

plt.title("Average IQ by country", fontsize=16)

plt.xlabel("Country", fontsize=14)
plt.ylabel("Average IQ", fontsize=14)
plt.show()


