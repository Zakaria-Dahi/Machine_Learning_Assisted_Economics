# http://www.datadependence.com/2016/06/creating-map-visualisations-in-python/
# http://boundingbox.klokantech.com/
# http://www.ine.es/dyngs/DataLab/manual.html?cid=45

import matplotlib.pyplot as plt
from random import randint
import matplotlib.cm
import pandas as pd
import numpy as np

# Creo que las dos siguientes no son necesarias
# sudo apt-get install python-mpltoolkits.basemap <- Este Python 2
# sudo apt install python3-mpltoolkits.basemap <- Este Python 3

# Estas dos son la bue
# sudo apt-get install libgeos-dev
# pip3 install https://github.com/matplotlib/basemap/archive/v1.1.0.zip
# En windows:
# instalar desde https://www.lfd.uci.edu/~gohlke/pythonlibs/
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize

# westlimit=-10.01; southlimit=35.07; eastlimit=4.88; northlimit=44.13

fig, ax = plt.subplots(figsize=(10, 20))

# resolution: The options are crude, low, intermediate, high or full.
# projection: https://matplotlib.org/basemap/users/mapsetup.html
# The ‘lat_0’ and ‘lon_0’ are the latitude and longitude of the centre point of your map.
#  ‘llcrnr’ stands for ‘lower left corner’ and ‘urcrnr’ stands for upper right corner.


m = Basemap(resolution='i',  # c, l, i, h, f or None
            projection='merc',
            lat_0=39.6, lon_0=-2.565,
            llcrnrlon=-10.01, llcrnrlat=35.07, urcrnrlon=4.88, urcrnrlat=44.13)

# Limites del mapaa
m.drawmapboundary(fill_color='#46bcec')
# Continente
m.fillcontinents(color='#f2f2f2', lake_color='#46bcec')
# Limites continente
m.drawcoastlines()

# http://centrodedescargas.cnig.es/CentroDescargas/catalogo.do?Serie=CAANE

# m.readshapefile('data/recintos_municipales_inspire_peninbal_etrs89/recintos_municipales_inspire_peninbal_etrs89', 'municipios')
m.readshapefile('data/recintos_provinciales_inspire_peninbal_etrs89/recintos_provinciales_inspire_peninbal_etrs89',
                'provincias')
# m.readshapefile('data/recintos_autonomicas_inspire_peninbal_etrs89/recintos_autonomicas_inspire_peninbal_etrs89', 'autonomias')
p = set()
for area in m.provincias_info:
    p.add(area['NAMEUNIT'])

print(p)


def set_value(city):
    if city == "Málaga":
        return 255
    else:
        return 0


df_poly = pd.DataFrame({
    'shapes': [Polygon(np.array(shape), True) for shape in m.provincias_info],
    'area': [area['NAMEUNIT'] for area in m.provincias_info],
    'count': [set_value(area["NAMEUNIT"]) for area in m.provincias_info]
})
# df_poly = df_poly.merge(new_areas, on='municipios', how='left')

cmap = plt.get_cmap('Oranges')
pc = PatchCollection(df_poly.shapes, zorder=2)
norm = Normalize()

pc.set_facecolor(cmap(norm(df_poly['count'].fillna(0).values)))
ax.add_collection(pc)

mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

mapper.set_array(df_poly['count'])
plt.colorbar(mapper, shrink=0.4)

plt.show()
