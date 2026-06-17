import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('lesson14.csv')

# Convert 'Population - 2023' to numeric, removing commas
df['Population - 2023'] = df['Population - 2023'].str.replace(',', '').astype(float)

print(df.info())

# Create an interactive bubble map
fig = px.scatter_geo(df, locations='Country', locationmode='country names',
                     hover_name='Country', size='Average IQ', color='Continent',
                     projection='natural earth', title='Average IQ by Country',
                     size_max=20, template='plotly_dark')
fig.show()

# Create the choropleth map with hover data
fig = px.choropleth(df, locations='Country', locationmode='country names',
                    color='Average IQ', hover_name='Country',
                    hover_data=['Literacy Rate', 'Nobel Prices'],
                    color_continuous_scale='agsunset',
                    projection='natural earth',
                    title='Average IQ by Country')

# Show the figure
fig.show()