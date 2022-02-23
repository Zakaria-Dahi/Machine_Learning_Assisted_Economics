#Import the necessary Python moduless
from random import randint
import pandas as pd
import geopandas as gpd
import numpy as np
from geopandas.tools import sjoin
import folium
from folium.plugins import MarkerCluster
# from folium.element import IFrame
import shapely
from shapely.geometry import Point
import unicodedata
import pysal as ps

# http://nbviewer.jupyter.org/github/python-visualization/folium/blob/master/examples/TimeSliderChoropleth.ipynb
# http://nbviewer.jupyter.org/github/python-visualization/folium/blob/master/examples/GeoJSON_and_choropleth.ipynb

#Read tracts shapefile into GeoDataFrame
tracts = gpd.read_file('data/recintos_municipales_inspire_peninbal_etrs89/recintos_municipales_inspire_peninbal_etrs89.shp') #.set_index('NAMEUNIT')
#print(len(tracts))
tracts['value'] = 0
# print(tracts)
# westlimit=-10.01; southlimit=35.07; eastlimit=4.88; northlimit=44.13
# center 39,6, -2.565
pop_map = folium.Map([39.6, -2.565], zoom_start=7)

# http://mattgoldwasser.com/posts/choroplot/
for i in range(len(tracts)):
    tracts.loc[i, ['value']] = randint(0,500)
    gs = folium.GeoJson(tracts.iloc[i:i + 1])
    label = '{}: {} personas'.format(tracts['NAMEUNIT'][i], tracts['value'][i])
    folium.Popup(label).add_to(gs)
    gs.add_to(pop_map)

# print(tracts.head(10))


pop_map.choropleth(
    geo_data=tracts.to_json(),
    name='choropleth',
    data=tracts,
    columns=['NAMEUNIT', 'value'],
    key_on='feature.properties.NAMEUNIT',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population',
    highlight=True
)


# Update basemap with choropleth
folium.LayerControl().add_to(pop_map) #Add layer control to toggle on/off
pop_map.save('pop.html') #save HTML


'''


fig, ax = plt.subplots(figsize=(10,20))

# resolution: The options are crude, low, intermediate, high or full.
# projection: https://matplotlib.org/basemap/users/mapsetup.html
# The ‘lat_0’ and ‘lon_0’ are the latitude and longitude of the centre point of your map.
#  ‘llcrnr’ stands for ‘lower left corner’ and ‘urcrnr’ stands for upper right corner.


m = Basemap(resolution='i', # c, l, i, h, f or None
            projection='merc',
            lat_0=39.6, lon_0=-2.565,
            llcrnrlon=-10.01, llcrnrlat=35.07, urcrnrlon=4.88, urcrnrlat=44.13)

# Limites del mapaa
m.drawmapboundary(fill_color='#46bcec')
# Continente
m.fillcontinents(color='#f2f2f2',lake_color='#46bcec')
# Limites continente
m.drawcoastlines()

#http://centrodedescargas.cnig.es/CentroDescargas/catalogo.do?Serie=CAANE

m.readshapefile('data/recintos_municipales_inspire_peninbal_etrs89/recintos_municipales_inspire_peninbal_etrs89', 'municipios')
# m.readshapefile('data/recintos_provinciales_inspire_peninbal_etrs89/recintos_provinciales_inspire_peninbal_etrs89', 'provincias')
# m.readshapefile('data/recintos_autonomicas_inspire_peninbal_etrs89/recintos_autonomicas_inspire_peninbal_etrs89', 'autonomias')

df_poly = pd.DataFrame({
        'shapes': [Polygon(np.array(shape), True) for shape in m.municipios],
        'area': [area['NAMEUNIT'] for area in m.municipios_info],
        'count': [randint(0,50) for area in m.municipios_info]
    })
#df_poly = df_poly.merge(new_areas, on='municipios', how='left')

cmap = plt.get_cmap('Oranges')
pc = PatchCollection(df_poly.shapes, zorder=2)
norm = Normalize()

pc.set_facecolor(cmap(norm(df_poly['count'].fillna(0).values)))
ax.add_collection(pc)

mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

mapper.set_array(df_poly['count'])
plt.colorbar(mapper, shrink=0.4)

plt.show()
'''
