import csv
import datetime
import functools
import itertools
import multiprocessing

import openmensa


def date_range(start, stop):
    while start <= stop:
        yield start.strftime("%Y-%m-%d")
        start += datetime.timedelta(days=1)


def date_ranges(start, stop, n):
    data = list(date_range(start, stop))
    return [data[i:i+n] for i in range(0, len(data), n)]


def fetch_date_range(dates, mensa_id):
    meals = []
    for date in dates:
        try:
            for meal in openmensa.fetch_meals(mensa_id, date):
                meals.append(meal)
        except Exception as e:
            print(f"fetching {mensa_id}/{date} errored: {e}")

    return meals


def dump_meals(meals, filename):
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=meals[0]._fields)
        writer.writeheader()

        for meal in meals:
            writer.writerow(meal._asdict())


def dump_mensa_to_csv(mensa_id, start, stop):
    ranges = date_ranges(start, stop, 50)
    with multiprocessing.Pool(processes=32) as pool:
        f = functools.partial(fetch_date_range, mensa_id=mensa_id)
        meals = pool.map(f, ranges)

    filename = f"{mensa_id}_{start}_{stop}.csv"

    meals = list(filter(lambda x: x is not None, meals))
    dump_meals(list(itertools.chain(*meals)), filename)


if __name__ == "__main__":
    start = datetime.date(2012, 7, 1)
    stop = datetime.date(2020, 2, 1)

    for mensa_id in range(113, 117):
        dump_mensa_to_csv(mensa_id, start, stop)
