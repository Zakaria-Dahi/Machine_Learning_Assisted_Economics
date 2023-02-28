import requests, json
from database import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from time import time

# CONSTANTS:
# milliseconds per day (24 hours/day * 60 minutes/hour * 60 seconds/minute * 1000 milliseconds)
DAY = 86400000


# Calculate the date of the next day in milliseconds
def next_day(d):
    return d + DAY


# Get a date in string format. If the date is invalid it is set to 0.
def get_date_string(d):
    if not d:
        d = 0
    d = d/1000.0  # we need it in seconds

    d1 = datetime.fromtimestamp(d)

    return d1.strftime("%Y%m%d")


# Get the current date (string format) in milliseconds
def get_current_date():
    return get_date_string(time() * 1000)


# Check if lst2 is a sublist of list1 (i.e., all elements of lst2 are in lst1)
def sublist(lst1, lst2):
    ls1 = [element for element in lst1 if element in lst2]
    return ls1 == lst1


# Given a series and a list of locations, it gets the codes to get the actual data.
# If location is not already in table, it is added
# session parameter allows to access to the database tables
def get_codes(serie, session, locations):
    # URL to get the codes
    template_url = 'http://servicios.ine.es/wstempus/js/ES/SERIES_OPERACION/{code}?page={page}'
    page = 1  # the codes can be divided into several pages
    cities = [*locations]  # convert to list

    # Check if all the codes are already in the database
    c = session.query(Code).filter(Code.serie_id == serie.id).count()
    if c == len(cities):
        print("f\tAll codes already found!")
        return

    # Main loop: while some city is not already found, continue the search
    while cities:
        # Prints the number of missing places and the place name if the number is small (< 5)
        print(f"\tPage {page} missing locations {len(cities)} ", end="")
        if len(cities) < 5:
            print(cities)
        else:
            print()
        # Get the data from the INE website
        url = template_url.format(code=serie.code, page=page)
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            break
        data = response.json()

        if len(data) == 0:
            # print("No data")
            break

        for x in data: # for each entry in the downloaded data
            code = x['COD']
            value = x['Nombre']
            # Check if the current entry is a city in our list
            # Since the names can be in different ways and includes information about the series,
            # we divide it in words and compare words (our considered city should be completely contained into the name)
            city = ""
            for loc in cities:
                locs = loc.split(" ")
                values = value.replace(",", ".")
                values = values.split(".")
                values = [e.strip() for e in values]
                if sublist(locs, values) or sublist([loc], values):
                    city = loc
                    break
            if city is "":
                continue

            # If we are here, it indicated that the city exists in our list

            # Remove the name of the city in the name to get the series name.
            rest = value.replace(",", '.')
            rest = rest.replace(city+'.', '')
            y = city.split(" ")
            for yy in y:
                rest = rest.replace(' '+yy+'.', '')
                rest = rest.replace(yy + '.', '')
            rest = rest.replace('  ', ' ')
            rest = rest.replace('  ', ' ')
            rest = rest.replace('  ', ' ')
            rest = rest.replace('  ', ' ')

            # If data contains the required text, we add the correspondent code
            # Only it is added the first code
            if serie.text in rest:
                print(f"\t Found: {city} in {value}")
                cities.remove(city)
                c = session.query(Code).filter(Code.location_id == locations[city], Code.serie_id == serie.id).first()
                if not c:
                    # print(f"Adding rest: {rest} code {code}")
                    c = Code(location_id=locations[city], serie_id=serie.id, code=code, text=value, real_date=0)
                    session.add(c)
                    session.commit()
        page += 1

    if cities:
        print(f"Some cities are missing: {cities}")
    else:
        print("All cities are found!")


# Gets the actual data (values) from INE website
def insert_values(session, results):
    template_url = "http://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{code}?date={d1}:{d2}"

    d2 = get_current_date() # Final date
    current_time = time()
    for code in results:
        print(f"  Adding values for code: {code.serie_id} - {code.location_id} -> ", end="")
        if not code.last_update:
            code.last_update = 0
        d1 = get_date_string(next_day(code.last_update)) # initial date
        url = template_url.format(code=code.code, d1=d1, d2=d2)
        # Get data from INE website
        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            break
        data = response.json()
        print(f"{len(data['Data'])} data ", end="")

        # Get the data
        for val in data['Data']:
            # Update codes tables
            if val['Fecha'] > code.last_update:
                code.last_update = val['Fecha']
            code.real_date = current_time
            print(".", end="")
            # Add the new value to values table
            v = Value(code_id=code.id, year=val['Anyo'], period=val['FK_Periodo'], value=val['Valor'])
            session.add(v)
        print()
        session.commit()


# Get the values for a concrete series
def get_values(serie, session):
    current_date = time() - DAY
    results = session.query(Code).filter(Code.serie_id == serie.id, Code.real_date < current_date).all()
    insert_values(session, results)


# Update the values for all the series
def update_values(session):
    current_date = time() - DAY
    results = session.query(Code).filter(Code.real_date < current_date).all()
    insert_values(session, results)


# Get data for a serie and set of localtions. If the series or codes are not in DB, they are inserted
def get_data(serie, session, locations):
    s = session.query(Serie).filter(Serie.name == serie.name).first()
    print('Analyzing serie ...')
    if not s:
        print(" Adding serie ...")
        session.add(serie)
        session.commit()
        s = serie
    print('Analyzing codes ...')
    c = session.query(Code).filter(Code.serie_id == s.id).first()
    if not c:
        print(' Adding codes ...')
        get_codes(s, session, locations)
    print('Adding values')
    get_values(s, session)


# Load locations from database
def load_locations(session):
    data = session.query(Location)
    locations = {}
    for x in data:
        locations[x.name] = x.id
    return locations


if __name__ == '__main__':
    engine = createDB()
    Session = sessionmaker(bind=engine)
    session = Session()
    locations = load_locations(session)

    with open('series.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for d in data:
            serie = Serie(name=d["name"], code=d["code"], text=d["text"])
            print(f"Getting {serie.name} codes")
            get_data(serie, session, locations)

    print(f"Updating data")
    update_values(session)
    print("Closing session")
