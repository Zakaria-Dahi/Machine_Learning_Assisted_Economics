import requests
'''
url_plantilla = 'http://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{codigo}?nult={num_datos}'

codigo = "EPA87"
num_datos = 4

url = url_plantilla.format(codigo=codigo, num_datos=num_datos)
respuesta = requests.get(url)
datos = respuesta.json()

print(datos['Nombre'])
for x in datos['Data']:
    fecha = datetime.date.fromtimestamp(
                      x['Fecha'] // 1000)
    ocupados = x['Valor']
    print(fecha, ocupados)
'''
from mpl_toolkits.basemap import Basemap
import pandas as pd
m = Basemap(resolution='i', # c, l, i, h, f or None
            projection='merc',
            lat_0=39.6, lon_0=-2.565,
            llcrnrlon=-10.01, llcrnrlat=35.07, urcrnrlon=4.88, urcrnrlat=44.13)

m.readshapefile('data/recintos_municipales_inspire_peninbal_etrs89/recintos_municipales_inspire_peninbal_etrs89', 'municipios')


df_poly = pd.DataFrame({
        'area': [area['NAMEUNIT'] for area in m.municipios_info],
        'count': [0 for area in m.municipios_info]
    })

url_plantilla = 'http://servicios.ine.es/wstempus/js/ES/SERIES_OPERACION/{codigo}?page={page}'


codigo = "22" # Población
page = 1
# http://servicios.ine.es/wstempus/js/ES/SERIES_OPERACION/22?page=2

# http://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP61412?nult=1

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
            if nombre  in df_poly['area'].values:
                municipios[nombre] = [code, 1]
            else:
                municipios[nombre] = [code, 0]
    page += 1

print(len(municipios),' de ',len(df_poly['area'].values))

for i in range(len(df_poly)):
    print(df_poly.at[i,'area'], ":", df_poly.at[i,'count'])

print("="*80)

for k,v in municipios.items():
    print(k,":",v[1],":",v[0])