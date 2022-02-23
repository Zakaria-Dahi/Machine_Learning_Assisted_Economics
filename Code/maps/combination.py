import matplotlib.pyplot as plt
import matplotlib.cm
import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
import requests


def createMap():
    fig, ax = plt.subplots(figsize=(10,20))
    m= Basemap(resolution='i', # c, l, i, h, f or None
              projection='merc',
              lat_0=39.6, lon_0=-2.565,
              llcrnrlon=-10.01, llcrnrlat=35.07, urcrnrlon=4.88, urcrnrlat=44.13)
    m.drawmapboundary(fill_color='#46bcec')
    m.fillcontinents(color='#f2f2f2', lake_color='#46bcec')
    m.drawcoastlines()

    return m, ax


def loadShpData(m):
    m.readshapefile('data/recintos_municipales_inspire_peninbal_etrs89/recintos_municipales_inspire_peninbal_etrs89', 'municipios')
    df_poly = pd.DataFrame({
            'shapes': [Polygon(np.array(shape), True) for shape in m.municipios],
            'area': [area['NAMEUNIT'] for area in m.municipios_info],
            'count': [0 for area in m.municipios_info]
            })
    return df_poly


def getAreas(df):
    url_plantilla = 'http://servicios.ine.es/wstempus/js/ES/SERIES_OPERACION/{codigo}?page={page}'

    codigo = "22"  # Población
    page = 1

    municipios = dict()
    while True:
        print("Página ", page)
        url = url_plantilla.format(codigo=codigo, page=page)
        respuesta = requests.get(url)
        if respuesta.status_code != 200:
            print(respuesta.status_code)
            break
        datos = respuesta.json()

        if len(datos) == 0:
            print("Sin datos")
            break

        for x in datos:
            code = x['COD']
            valores = x['Nombre'].split('.')
            if len(valores) < 3:
                continue
            nombre = valores[0]
            tipo = valores[2]
            a = nombre.split(',')
            nombre = ''
            for b in a:
                nombre = b.strip() + " " + nombre
            nombre = nombre.strip()
            if tipo.strip() == "Total":
                if nombre in df['area'].values:
                    municipios[nombre] = [code, 1]
                else:
                    municipios[nombre] = [code, 0]
        page += 1
    return municipios


def loadPopData(df, mun):
    url_plantilla = 'http://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{codigo}?nult=1'

    for k,v in mun.items():
        if v[1] == 1:
            print("Loading data from ", k)
            url = url_plantilla.format(codigo=v[0])
            respuesta = requests.get(url)
            if respuesta.status_code != 200:
                print(respuesta.status_code)
                continue
            datos = respuesta.json()

            if len(datos) == 0:
                print("Sin datos")
                continue
            df.loc[df['area'] == k, ['count']] = datos['Data'][0]['Valor']



def drawMap(df, ax):
    cmap = plt.get_cmap('Oranges')
    pc = PatchCollection(df.shapes, zorder=2)
    norm = Normalize()

    pc.set_facecolor(cmap(norm(df['count'].fillna(0).values)))
    ax.add_collection(pc)

    mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

    mapper.set_array(df['count'])
    plt.colorbar(mapper, shrink=0.4)

    plt.show()


if __name__ == "__main__":
    print("Creating Map...")
    m, axes = createMap()
    print("Loading shapes...")
    df = loadShpData(m)
    print("Getting areas...")
    mun = getAreas(df)
    print("Loading population data...")
    loadPopData(df, mun)
    print("Drawing map...")
    drawMap(df, axes)