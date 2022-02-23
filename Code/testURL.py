import requests
from time import sleep

def get_types(code1):
    template_url = 'http://servicios.ine.es/wstempus/js/ES/SERIES_OPERACION/{code}?page={page}'
    page = 1
    city = "Valencia/València"
    while 1:
        url = template_url.format(code=code1, page=page)
        print(f"\tPage {page}")
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            if response.status_code/500 >= 1:
                sleep(1)
                continue
            else:
                break
        data = response.json()

        if len(data) == 0:
            print("No data")
            break

        for x in data:
            code = x['COD']
            value = x['Nombre']
            if city not in value:
                continue
            print(f"\t\t{code} - {value}")
        page += 1


if __name__ == '__main__':
    # All posible
    names = {353 : "Atlas de Distribución de Renta de los Hogares", 72 : "Cifras de Población", 22 : "Cifras Oficiales de Población de los Municipios Españoles: Revisión del Padrón Municipal", 345 : "Contabilidad nacional anual de España: agregados por rama de actividad", 247 : "Contabilidad Nacional de España. Base 2010", 237 : "Contabilidad Nacional Trimestral de España: Principales Agregados", 20 : "Contabilidad Nacional Trimestral de España. Base 2000", 51 : "Contabilidad Nacional Trimestral de España. Base 2008", 246 : "Cuentas Trimestrales no Financieras de los Sectores Institucionales", 49 : "Distribución de Apellidos", 16 : "Distribución de Nombres", 139 : "Encuesta Anual de Coste Laboral", 140 : "Encuesta Anual de Estructura Salarial", 249 : "Encuesta Coyuntural sobre Stocks y Existencias", 155 : "Encuesta de Condiciones de Vida (ECV)", 30 : "Encuesta de coyuntura de comercio al por menor. Base 1994", 329 : "Encuesta de Gasto Turístico", 328 : "Encuesta de Ocupación en Albergues", 241 : "Encuesta de Ocupación en Alojamientos de Turismo Rural", 39 : "Encuesta de Ocupación en Alojamientos Turísticos", 239 : "Encuesta de Ocupación en Apartamentos Turísticos", 240 : "Encuesta de Ocupación en Campings", 238 : "Encuesta de Ocupación Hotelera", 293 : "Encuesta de Población Activa (EPA)", 314 : "Encuesta de Presupuestos Familiares (EPF)", 334 : "Encuesta de turismo de residentes", 93 : "Encuesta Industrial Anual de Productos", 44 : "Encuesta sobre Comercio Internacional de Servicios y otras Operaciones Internacionales", 303 : "Encuesta Trimestral de Coste Laboral (ETCL)", 336 : "Estadística de Adquisiciones de Nacionalidad Española de Residentes", 213 : "Estadística de Condenados: Adultos", 214 : "Estadística de Condenados: Menores", 23 : "Estadística de Defunciones según la Causa de Muerte", 4 : "Estadística de Efectos de Comercio Impagados", 40 : "Estadística de Hipotecas", 212 : "Estadística de Juzgados de Paz", 71 : "Estadística de Migraciones", 234 : "Estadística de Movilidad Laboral y Geográfica", 66 : "Estadística de Nulidades, Separaciones y Divorcios", 125 : "Estadística de Sociedades Mercantiles", 7 : "Estadística de Transmisión de Derechos de la Propiedad", 297 : "Estadística de Transporte de Viajeros", 215 : "Estadística de Violencia Doméstica y Violencia de Género", 13 : "Estadística del Procedimiento Concursal", 256 : "Estadística Estructural de Empresas: Sector Comercio", 24 : "Estadística Estructural de Empresas: Sector Industrial", 130 : "Estadística Estructural de Empresas: Sector Servicios", 259 : "Estadística sobre Ejecuciones Hipotecarias", 171 : "Estadística sobre Transporte Ferroviario", 21 : "Estimaciones de la Población Actual (ePOBa)", 43 : "Explotación Estadística del Directorio Central de Empresas", 205 : "Flujos de la Población Activa", 31 : "Indicadores de Actividad del Sector Servicios", 163 : "Indicadores de Confianza Empresarial", 180 : "Indicadores de Rentabilidad del Sector Hotelero", 33 : "Indicadores Demográficos Básicos", 10 : "Indicadores Urbanos", 258 : "Índice de Cifra de Negocios Empresarial", 6 : "Índice de Coste Laboral Armonizado", 331 : "Índice de Garantía de la Competitividad", 254 : "Índice de ingresos hoteleros", 63 : "Índice de Precios de Alojamientos de Turismo Rural", 61 : "Índice de Precios de Apartamentos Turísticos", 62 : "Índice de Precios de Camping", 25 : "Índice de Precios de Consumo (IPC)", 18 : "Índice de Precios de Consumo Armonizado (IPCA)", 15 : "Índice de Precios de la Vivienda (IPV)", 137 : "Índice de Precios del Trabajo", 132 : "Índice de Precios Hoteleros", 42 : "Índices de Cifras de Negocios", 32 : "Índices de Comercio al por Menor", 41 : "Índices de Entradas de Pedidos", 48 : "Índices de Precios de Exportación y de Importación de Productos Industriales", 104 : "Índices de Precios de Materiales y Energía e Índices Nacionales de la Mano de Obra", 14 : "Índices de Precios del Sector Servicios", 27 : "Índices de Precios Industriales", 26 : "Índices de Producción Industrial", 309 : "MNP Estadística de Defunciones", 305 : "MNP Estadística de Matrimonios", 307 : "MNP Estadística de Nacimientos", 330 : "Movimientos Turísticos en Fronteras", 333 : "Mujeres y Hombres en España", 36 : "Poblaciones de derecho desde 1986 hasta 1995. Cifras oficiales sacadas del Padrón.", 35 : "Poblaciones de hecho desde 1900 hasta 1991. Cifras oficiales sacadas de los Censos respectivos.", 52 : "Proyecciones de Población a Corto Plazo", 54 : "Proyecciones de Población a Largo Plazo", 197 : "Tablas de Mortalidad"}
    # codes = [72, 22, 345, 247, 237, 20, 51, 246, 49, 16, 139, 140, 249, 155, 30, 329, 328, 241, 39, 239, 240, 238, 293, 314, 334, 93, 44, 303, 336, 213, 214, 23, 4, 40, 212, 71, 234, 66, 125, 7, 297, 215, 13, 256, 24, 130, 259, 171, 21, 43, 205, 31, 163, 180, 33, 10, 258, 6, 331, 254, 63, 61, 62, 25, 18, 15, 137, 132, 42, 32, 41, 48, 104, 14, 27, 26, 309, 305, 307, 330, 333, 36, 35, 52, 54, 197, 353]
    # After the first complete analysis using Albacete as location, maybe this is the most interesting data information
    codes = [10, 25, 43, 293]
    codes.sort()
    for code in codes:
        if code > 292:
            print(f"Searching in {code} - {names[code]}")
            get_types(code)