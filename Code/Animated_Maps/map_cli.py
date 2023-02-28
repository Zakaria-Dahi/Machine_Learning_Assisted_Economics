# coding: latin-1

import getopt
import os
import re
import sys
import xml.etree.ElementTree as ET
import logging

import matplotlib.cm
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from sqlalchemy import func

from cleanData import get_reduced_database, Data

series = ["Alimentos y bebidas no alcohólicas. Índice.", "Bebidas alcohólicas y tabaco. Índice.",
          "Comunicaciones. Índice.", "De 1 a 2. Total de empresas. Total CNAE. Empresas.",
          "De 10 a 19. Total de empresas. Total CNAE. Empresas.",
          "De 100 a 199. Total de empresas. Total CNAE. Empresas.",
          "De 1000 a 4999. Total de empresas. Total CNAE. Empresas.",
          "De 20 a 49. Total de empresas. Total CNAE. Empresas.",
          "De 200 a 499. Total de empresas. Total CNAE. Empresas.",
          "De 3 a 5. Total de empresas. Total CNAE. Empresas.", "De 50 a 99. Total de empresas. Total CNAE. Empresas.",
          "De 500 a 999. Total de empresas. Total CNAE. Empresas.",
          "De 5000 o más asalariados. Total de empresas. Total CNAE. Empresas.",
          "De 6 a 9. Total de empresas. Total CNAE. Empresas.", "Enseñanza. Índice.", "Men Activity Percentage",
          "Men Employment Percentage", "Men Unemployment Percentage", "Men employment Percentage",
          "Ocio y cultura. Índice.", "Otros bienes y servicios. Índice.", "Restaurantes y hoteles. Índice.",
          "Sanidad. Índice.", "Sin asalariados. Total de empresas. Total CNAE. Empresas.",
          "Total. Total de empresas. Total CNAE. Empresas.", "Transporte. Índice.", "Vestido y calzado. Índice.",
          "Women Activity Percentage", "Women Employment  Percentage", "Women Unemployment  Percentage",
          "Women Unemployment Percentage", "Women employment Percentage", "Índice general. Variación mensual."]


def get_data(arguments):
    session = get_reduced_database()
    res = session.query(Data). \
        filter(Data.year == int(arguments["year"])). \
        filter(Data.period == int(arguments["period"])). \
        filter(Data.serie_name == arguments["series"]). \
        all()
    data = {}
    for r in res:
        data[r.location_name] = r.value

    if len(data) == 0:
        print("No values found!")
        sys.exit(0)

    return data


def get_min_max_values(arguments):
    session = get_reduced_database()
    res = session.query(func.max(Data.value).label("max_value"),
                        func.min(Data.value).label("min_value"), ). \
        filter(Data.serie_name == arguments["series"]). \
        one()
    return res.min_value, res.max_value


def tuple2color(t):
    color = "#"
    for i in range(3):
        c = hex(int(t[i] * 255))[2:]
        if len(c) == 1:
            c = "0" + c
        color += c
    return color


def colorize_map(names, colors):
    tree = ET.parse('map.svg')
    root = tree.getroot()
    for child in root:
        if child.attrib["id"] in names:
            i = names.index(child.attrib["id"])
            t = child.attrib["style"]
            p = re.compile(r"fill:(.*?);")
            tb = p.sub(f"fill:{tuple2color(colors[i])};", t)
            child.set("style", tb)
    tree.write("_map.svg")


def scale(drawing):
    """
    Scale a reportlab.graphics.shapes.Drawing()
    object while maintaining the aspect ratio
    """
    scaling_x = 1920 / drawing.minWidth()
    scaling_y = scaling_x

    drawing.width = drawing.minWidth() * scaling_x
    drawing.height = drawing.height * scaling_y
    drawing.scale(scaling_x, scaling_y)
    return drawing


def define_ticks(cbar, data_lst, vmin, vmax):
    m0 = int(vmin)  # colorbar min value
    m4 = int(vmax)  # colorbar max value
    m1 = int(1 * (m4 - m0) / 4.0 + m0)  # colorbar mid value 1
    m2 = int(2 * (m4 - m0) / 4.0 + m0)  # colorbar mid value 2
    m3 = int(3 * (m4 - m0) / 4.0 + m0)  # colorbar mid value 3
    cbar.set_ticks([m0, m1, m2, m3, m4])
    labels = [m0, m1, m2, m3, m4]
    factor_letter = ''
    d = 1
    if m0 > 1000000:
        factor_letter = 'M'
        d = 1000000
    elif m0 > 1000:
        factor_letter = 'K'
        d = 1000

    labels2 = [f"{int(k/d)}{factor_letter}" for k in labels]

    cbar.set_ticklabels(labels2)


def create_image(norm, cmap, data_lst, args, vmin, vmax):
    drawing = svg2rlg("_map.svg")
    drawing = scale(drawing)
    renderPM.drawToFile(drawing, "_map.png", fmt="PNG")
    img = plt.imread('_map.png')
    fig, ax = plt.subplots()
    ax.set_axis_off()
    ax.imshow(img)
    mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

    mapper.set_array(data_lst)
    cb_axes = fig.add_axes([0.175, 0.2, 0.1, 0.65])
    cb_axes.set_axis_off()
    c_bar = plt.colorbar(mapper, ax=cb_axes, shrink=0.4)
    define_ticks(c_bar, data_lst, vmin, vmax)

    if args["show-date"]:
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        textstr = month[int(args["period"])]+"-"+str(args["year"])
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.75, 0.1, textstr, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

    plt.savefig(args["output"], bbox_inches='tight', dpi=300)
    plt.cla()
    plt.close(fig)
    os.remove("_map.svg")
    os.remove("_map.png")


def main(args):
    data = get_data(args)
    data_lst = list(data.values())
    name_lst = [n.replace(" ", "_") + "_path" for n in data.keys()]
    cmap = plt.get_cmap('YlOrRd')
    if not args["global"]:
        vmin = min(data_lst)
        vmax = max(data_lst)
    else:
        vmin, vmax = get_min_max_values(args)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    color = cmap(norm(data_lst))
    colorize_map(name_lst, color)
    create_image(norm, cmap, data_lst, args, vmin, vmax)


def show_help():
    print("""Options:
    -h | --help \t\t\t This help
    -g | --global \t\t\t Global Min/Max values of value [False by default]
    -d | --show-date \t\t\t Show the date in the image [False by default]
    -y | --year <year> \t\t\t From 2003 to 2017 [2010 by default]
    -p | --period <period> \t\t From 0 to 11
    -s | --series <series name> \t [Total. Total de empresas. Total CNAE. Empresas. by default]
    -o | --output <output file> \t [output.png by default]""")
    print("Data series available:")
    for s in series:
        print(f"\t{s}")


def parse_args(argv):
    arguments = {
        "year": 2010,
        "period": 0,
        "series": 'Total. Total de empresas. Total CNAE. Empresas.',
        "output": "output.png",
        "global": False,
        "show-date": False
    }
    try:
        opts, args = getopt.getopt(argv, "hy:p:s:o:dg", ["year=", "period=", "series=", "output=", "help"])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', "--help"]:
            show_help()
            sys.exit()
        elif opt in ("-y", "--year"):
            arguments["year"] = arg
        elif opt in ("-p", "--period"):
            arguments["period"] = arg
        elif opt in ("-s", "--series"):
            arguments["series"] = arg
        elif opt in ("-o", "--output"):
            arguments["output"] = arg
        elif opt in ["-g", "--global"]:
            arguments["global"] = True
        elif opt in ["-d", "--show-date"]:
            arguments["show-date"] = True
    return arguments


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    args = parse_args(sys.argv[1:])
    main(args)
