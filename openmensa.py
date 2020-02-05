#!/usr/bin/env python3

import collections
import csv
import datetime
import functools
import http.client
import itertools
import json
import multiprocessing


""" Meal is a simple namedtuple class to store a single meal. """
Meal = collections.namedtuple("Meal", [
    "mensa_id", "date",
    "meal_id", "name", "category", "price_student", "notes"])


def fetch_meals(mensa_id, date):
    """ Fetch all meals for one mensa, identified by its id, at one specific
        date, formated as "yyyy-mm-dd".
    """
    def parse_meal(raw_meal, mensa_id, date):
        return Meal(
                mensa_id=mensa_id,
                date=date,
                meal_id=raw_meal["id"],
                name=raw_meal["name"],
                category=raw_meal["category"],
                price_student=raw_meal["prices"]["students"],
                notes=raw_meal["notes"])

    conn = http.client.HTTPSConnection("openmensa.org")
    conn.request("GET", f"/api/v2/canteens/{mensa_id}/days/{date}/meals")
    resp = conn.getresponse()

    if resp.status != 200:
        raise ValueError(f"http status {resp.status} != 200")

    raw_meals = json.loads(resp.read())
    return [parse_meal(raw_meal, mensa_id, date) for raw_meal in raw_meals]


def fetch_mensas(mensa_ids):
    """ Create a dict of ID -> name for all given mensa_ids. """
    ids = ','.join(map(str, mensa_ids))

    conn = http.client.HTTPSConnection("openmensa.org")
    conn.request("GET", f"/api/v2/canteens/?ids={ids}")
    resp = conn.getresponse()

    if resp.status != 200:
        raise ValueError(f"http status {resp.status} != 200")

    mensas = json.loads(resp.read())
    return {int(mensa["id"]): mensa["name"] for mensa in mensas}


def meals_set_mensa_name(meals, strip_prefix):
    """ Replace the mensa_id in all meals with the mena's name. A prefix, which
        might be the town's name, can be passed to be stripped.
    """
    mensa_ids = {meal.mensa_id for meal in meals}
    mensa_names = fetch_mensas(list(mensa_ids))
    mensa_names = {k: v.replace(strip_prefix, "", 1) for k, v in mensa_names.items()}

    return[meal._replace(mensa_id=mensa_names[meal.mensa_id]) for meal in meals]


def date_ranges(start, stop, n):
    """ List all dates as a "yyyy-mm-dd" str between start and stop. """
    data = []
    while start <= stop:
        data.append(start.strftime("%Y-%m-%d"))
        start += datetime.timedelta(days=1)

    return [data[i:i+n] for i in range(0, len(data), n)]


def fetch_date_range(dates, mensa_id):
    """ Create Meals for all dates at the specified mensa. """
    meals = []
    for date in dates:
        try:
            for meal in fetch_meals(mensa_id, date):
                meals.append(meal)
        except Exception as e:
            print(f"fetching {mensa_id}/{date} errored: {e}")

    return meals


def dump_mensa_to_csv(mensa_id, mensa_prefix, start, stop):
    """ Download all meals between start and stop in parallel and dump it as a
        CSV file. The filename will be returned.
    """
    ranges = date_ranges(start, stop, 50)
    with multiprocessing.Pool(processes=32) as pool:
        f = functools.partial(fetch_date_range, mensa_id=mensa_id)
        meals = pool.map(f, ranges)

    filename = f"{mensa_id}_{start}_{stop}.csv"

    meals = list(filter(lambda x: x is not None, meals))
    meals = list(itertools.chain(*meals))
    meals = meals_set_mensa_name(meals, mensa_prefix)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=meals[0]._fields)
        writer.writeheader()

        for meal in meals:
            writer.writerow(meal._asdict())

    return filename


if __name__ == "__main__":
    start = datetime.date(2012, 7, 1)
    stop = datetime.date(2020, 2, 7)
    mensas = range(113, 117)
    mensa_prefix = "Marburg, "

    csv_files = []
    for mensa_id in range(113, 117):
        csv_files.append(dump_mensa_to_csv(mensa_id, "Marburg, ", start, stop))

    print("Dumped {}".format(", ".join(csv_files)))
