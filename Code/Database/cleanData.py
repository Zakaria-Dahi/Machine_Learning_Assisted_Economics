from database import *
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base1 = declarative_base()


# Reduced database declaration
class Data(Base1):
    __tablename__ = 'data'

    id = sa.Column(sa.Integer, primary_key=True)
    location_name = sa.Column(sa.String)
    serie_name = sa.Column(sa.String)
    year = sa.Column(sa.Integer)
    period = sa.Column(sa.Integer)
    value = sa.Column(sa.Float)


def get_new_database():
    engine = sa.create_engine('sqlite:///db-reduced.db', encoding='latin1', echo=False)
    Base1.metadata.drop_all(engine)
    Base1.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_reduced_database():
    engine = sa.create_engine('sqlite:///db-reduced.db', encoding='latin1', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_amount_locations(session):
    return session.query(Location).count()


def get_locations(session):
    return session.query(Location)


def get_series_without_data(session):
    series = session.query(Serie).filter()
    result = []
    for s in series:
        codes = int(session.query(Code).filter(Code.serie_id == s.id).count())
        if codes == 0:
            result.append(s.name)
    return result


def get_series_without_data_for_all_locations(session, number):
    series = session.query(Serie).filter()
    result = []
    for s in series:
        codes = int(session.query(Code).filter(Code.serie_id == s.id).count())
        if codes > 0 and codes < number:
            result.append(s.name)
    return result


def get_adequate_series(session, number):
    series = session.query(Serie).filter()
    result = []
    for s in series:
        codes = int(session.query(Code).filter(Code.serie_id == s.id).count())
        if codes == number:
            result.append(s)
    return result


def print_list(text: object, l: object) -> object:
    if not l:
        print(f"{text}: None")
    else:
        print(f"{text}:")
        for s in l:
            print(f"\t{s}")


def test_data_per_series(session, series):
    final_result = []
    for s in series:
        codes = session.query(Code).filter(Code.serie_id == s.id).all()
        res = set()
        for code in codes:
            res.add(session.query(Value).filter(Value.code_id == code.id).count())
        if len(res) != 1:
            msg = f"{s.name} has locations with different amount of values: {res}"
        else:
            msg = f"{s.name} has all the locations with the same amount of values: {res}"
        final_result.append(msg)


def years_range_per_series(session, series):
    final_result = []
    for s in series:
        print(".", end="")
        codes = session.query(Code).filter(Code.serie_id == s.id).all()
        res = None
        for code in codes:
            values = {s.year for s in session.query(Value.year.distinct().label("year")).filter(Value.code_id == code.id).all()}
            if not res:
                res = values
            else:
                res = res.intersection(values)

        res = list(res)
        res.sort()
        i = 0
        min_year = None
        max_year = None
        while i < len(res)-1:
            if not min_year and res[i] == res[i+1]-1:
                min_year = res[i+1]
            if not max_year and res[-1-i] == res[-2-i]+1:
                max_year = res[-i-2]
            if min_year and max_year:
                break
            i += 1

        final_result.append({
            "serie": s,
            "min": min_year,
            "max": max_year,
            "years": res,
            "text": f"{s.name} from {min_year} to {max_year}: {res}"
        })
    print()
    return final_result


def filter_by_years(years, y1, y2):
    a = []
    for s in years:
        min_index = s["years"].index(s["min"])
        max_index = s["years"].index(s["max"])
        non_diff = (s["max"] - s["min"]) == (max_index - min_index)
        if s["min"] <= y1 and s["max"] >= y2 and non_diff:
            a.append(s)
    return a


def generate_values(amount, previous, last):
    if amount == 0:
        return [last]
    lst = []
    m = (last - previous) / (amount+1)
    for i in range(amount):
        lst.append(m*(i+1) + previous)
    lst.append(last)
    return lst


def create_new_values(years, locations, session, miny, maxy):
    s2 = get_new_database()
    s_counter = 0
    for s in years:
        print(f"Serie: {s_counter}")
        s_counter += 1
        l_counter = 0
        for l in locations:
            print(f"\tLocation {l_counter}")
            l_counter += 1
            code = session.query(Code).filter(Code.serie_id == s["serie"].id, Code.location_id == l.id).first()
            previous_row = session.query(Value).filter(Value.code_id == code.id, Value.year == miny-1).order_by(Value.period.desc()).first()
            previous =  previous_row.value
            for y in range(miny, maxy+1):
                values = session.query(Value).filter(Value.code_id == code.id, Value.year == y).order_by(Value.period.asc()).all()
                if len(values) > 12:
                    print(s["serie"].name)
                    for i in values:
                        print(f"{i.code_id} {i.year} - {i.period} -> {i.value}")
                    exit(-1)
                values_list = []
                for v in values:
                    values_list.append(v.value)
                missing_values = [0 for xl in values_list]
                while sum(missing_values) + len(values_list) < 12:
                    missing_values[missing_values.index(min(missing_values))] += 1
                final_list = []
                for i in range(len(missing_values)):
                    final_list += generate_values(missing_values[i],previous,values_list[i])
                    previous = values_list[i]
                # print(f"Ini: {values_list} end: {final_list} pre: {previous}")
                for i in range(len(final_list)):
                    v = Data(serie_name=s["serie"].name, year=y, period=i, value=final_list[i], location_name=l.name)
                    s2.add(v)
                s2.commit()


def get_extreme_years(years):
    min_year = 0
    max_year = 3000
    for y in years:
        if min_year < y["min"]:
            min_year = y["min"]
        if max_year > y["max"]:
            max_year = y["max"]
    return min_year, max_year


if __name__ == '__main__':
    engine = createDB()
    Session = sessionmaker(bind=engine)
    session = Session()

    nlocations = get_amount_locations(session)

    res = get_series_without_data(session)
    print_list("Series without data", res)
    res = get_series_without_data_for_all_locations(session, nlocations)
    print_list("Series without data for all the locations", res)

    series = get_adequate_series(session, nlocations)
    print_list("Considered series", [n.name for n in series])

#    res = test_data_per_series(session, series)
#    print_list("Amount of data per series", res)
    years = years_range_per_series(session, series)
    print_list("Years per series", [n["text"] for n in years])

    years = filter_by_years(years, 2003, 2013)
    print_list("Years per series (filtered)", [n["text"] for n in years])

    (min_year, max_year) = get_extreme_years(years)
    print(f"Considered years: {min_year}-{max_year}")

    locations = get_locations(session)

    create_new_values(years, locations, session, min_year, max_year)
