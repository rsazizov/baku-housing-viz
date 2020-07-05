import streamlit as st
import pandas as pd
import numpy as np

import pydeck

'''
## Baku Housing Visualization
'''

df = pd.read_csv('housing.csv')

view = pydeck.data_utils.compute_view(df[["lon", "lat"]])
view.pitch = 0
view.bearing = 0

min = st.sidebar.slider('Starting price (k AZN)', 0, df.price_val.max() // 1000)
max = st.sidebar.slider('Ending price (k AZN)', 0, df.price_val.max() // 1000,
                        df.price_val.max() // 1000)

price_type = st.sidebar.selectbox(
  'Price',
  ('Full', 'Per m2', 'Per room')
)

plot_type = st.sidebar.selectbox(
  'Plot type',
  ('Column', 'Scatter', 'Heatmap')
)

COLOR_BREWER_BLUE_SCALE = [
    [240, 249, 232],
    [204, 235, 197],
    [168, 221, 181],
    [123, 204, 196],
    [67, 162, 202],
    [8, 104, 172],
]

filter_df = df[(df.price_val >= min * 1000) & (df.price_val <= max * 1000)]
filter_df = filter_df.copy()

if price_type == 'Per m2':
  filter_df.price_val /= filter_df.area
elif price_type == 'Per room':
  filter_df.price_val /= filter_df.rooms

if plot_type == 'Scatter':
  column_layer = pydeck.Layer(
      "ScatterplotLayer",
      data=filter_df,
      get_position=["lon", "lat"],
      get_radius=200,
      pickable=True,
      get_fill_color=(180, 0, 200, 140),
      auto_highlight=True,
  )
elif plot_type == 'Column':
  column_layer = pydeck.Layer(
      "ColumnLayer",
      data=filter_df,
      get_position=["lon", "lat"],
      get_elevation="price_val",
      elevation_scale=5 if price_type == 'Per m2' else 0.005,
      radius=20,
      pickable=True,
      get_fill_color=(180, 0, 200, 140),
      auto_highlight=True,
  )

  view.pitch = 75
  view.bearing = 60

elif plot_type == 'Heatmap':
  column_layer = pydeck.Layer(
    "HeatmapLayer",
    data=filter_df,
    opacity=0.9,
    get_position=["lon", "lat"],
    aggregation='"MEAN"',
    color_range=COLOR_BREWER_BLUE_SCALE,
    threshold=1,
    get_weight='price_val',
    pickable=True,
  )

tooltip = {
    "html": "<b>{price_val}</b> AZN",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}

r = pydeck.Deck(
  column_layer, initial_view_state=view, 
  map_style="mapbox://styles/mapbox/dark-v9",
  tooltip=tooltip
)

st.write(r)