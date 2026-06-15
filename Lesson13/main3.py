import pandas as pd

data = {'name': ["Gerti", "Donjeta", "Aniku"],
        'age': [18, 55, 58],
        'City': ["Pr", "Malisheves", "Deqanit"]

        }
df = pd.DataFrame(data)

print(df)

fajlli = pd.read_csv('dataCSV.csv')

print(fajlli)