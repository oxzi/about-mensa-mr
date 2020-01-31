import collections
import http.client
import json


Meal = collections.namedtuple("Meal", [
    "mensa_id", "date",
    "meal_id", "name", "category", "price_student", "notes"])


def fetch_meals(mensa_id, date):
    conn = http.client.HTTPSConnection("openmensa.org")
    conn.request("GET", f"/api/v2/canteens/{mensa_id}/days/{date}/meals")
    resp = conn.getresponse()

    if resp.status != 200:
        raise ValueError(f"http status {resp.status} != 200")

    raw_meals = json.loads(resp.read())
    return [parse_meal(raw_meal, mensa_id, date) for raw_meal in raw_meals]


def parse_meal(raw_meal, mensa_id, date):
    return Meal(
            mensa_id=mensa_id,
            date=date,
            meal_id=raw_meal["id"],
            name=raw_meal["name"],
            category=raw_meal["category"],
            price_student=raw_meal["prices"]["students"],
            notes=raw_meal["notes"])
