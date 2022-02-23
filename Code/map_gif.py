# coding: latin-1

import getopt
import os
import imageio
import sys
import map_cli
import logging

from pygifsicle import optimize


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


def main(args):
    from PIL import Image
    with imageio.get_writer(args["output"], mode='I', duration=0.25) as writer:
        for y in range(2003, 2018):
            for p in range(12):
                arguments = {
                    "year": y,
                    "period": p,
                    "series": args["series"],
                    "output": f"_output{y}-{p}.png",
                    "global": True,
                    "show-date": True
                }
                print(f"Frame: _output{y}-{p}.png")
                map_cli.main(arguments)
                foo = Image.open(f"_output{y}-{p}.png")
                w, h = foo.size[0]//2, foo.size[1]//2
                foo = foo.resize((w, h), Image.ANTIALIAS)
                foo.save(f"_output{y}-{p}.png", optimize=True, quality=95)
                image = imageio.imread(f"_output{y}-{p}.png")
                writer.append_data(image)
                os.remove(f"_output{y}-{p}.png")
    optimize(args["output"])



def show_help():
    print("""Options:
    -h | --help \t\t\tThis help
    -s | --series <series name> \t [Total. Total de empresas. Total CNAE. Empresas. by default]
    -o | --output <output file> \t [output.gif by default]""")
    print("Data series available:")
    for s in series:
        print(f"\t{s}")


def parse_args(argv):
    arguments = {
        "series": 'Total. Total de empresas. Total CNAE. Empresas.',
        "output": "output.gif"
    }
    try:
        opts, args = getopt.getopt(argv, "hy:p:s:o:", ["year=", "period=", "series=", "output=", "help"])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', "--help"]:
            show_help()
            sys.exit()
        elif opt in ("-s", "--series"):
            arguments["series"] = arg
        elif opt in ("-o", "--output"):
            arguments["output"] = arg
    return arguments


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    args = parse_args(sys.argv[1:])
    main(args)
