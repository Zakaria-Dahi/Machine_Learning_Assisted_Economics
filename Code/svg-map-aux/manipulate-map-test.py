# coding: latin-1
import xml.etree.ElementTree as ET
import re
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

cities = ['Ninguna', 'Melilla', 'Ceuta', 'Zaragoza', 'Zamora', 'Valladolid', 'Valencia/València', 'Toledo', 'Teruel', 'Tarragona', 'Soria', 'Sevilla', 'Segovia', 'Santa Cruz de Tenerife', 'Salamanca', 'La Rioja', 'Pontevedra', 'Las Palmas', 'Palencia', 'Ourense', 'Navarra', 'Murcia', 'Málaga', 'Madrid', 'Lugo', 'Lleida', 'León', 'Jaén', 'Huesca', 'Huelva', 'Guadalajara', 'Granada', 'Girona', 'Gipuzkoa', 'Cuenca', 'A Coruña', 'Córdoba', 'Ciudad Real', 'Castellón/Castelló', 'Cantabria', 'Cádiz', 'Cáceres', 'Burgos', 'Bizkaia', 'Barcelona', 'Illes Balears', 'Badajoz', 'Ávila', 'Asturias', 'Araba/Álava', 'Almería', 'Alicante/Alacant', 'Albacete']


cities_completer = WordCompleter(cities)

tree = ET.parse('Provinces_of_Spain.svg')
root = tree.getroot()
print(root.tag)
c=set()
#s = {'#808000', '#00aa44', '#ff7f2a', 'none', '#ff5555', '#cccccc', '#ffd42a', '#5555ff'}
s = {'#00aa44', '#ff7f2a', '#ff5555', '#ffd42a', '#5555ff'}
for child in root:
    # if child.tag == '{http://www.w3.org/2000/svg}text':
    #    for child2 in child:
    #        c.add(child2.text)
    if child.tag == '{http://www.w3.org/2000/svg}path':
        t = child.attrib["style"]
        ta = re.search("fill:(.*?);", t).group(1)
        if ta in s:
            p = re.compile(r"fill:(.*?);")
            tb = p.sub("fill:#ff00ff;", t)
            child.set("style", tb)
            tree.write("test.svg")
            text = prompt('Enter city: ', completer=cities_completer)
            child.set("style", t)
            if text and text != "Ninguna":
                text = text.replace(" ", "_")
                child.set("id", text+"_path")

tree.write("map.svg")