from faker import Faker
from multiprocessing import Pool
from shapely import Point
import json
import random
from uuid import uuid4
DATA_OUT="./data/locations.json"
NUM_DOCS=1000000
NUM_WORKERS=20

random.seed(0)
Faker.seed(0)
fake = Faker()

def generate():
    ndocs = [NUM_DOCS // NUM_WORKERS for _ in range(NUM_WORKERS)]
    ndocs[0] += NUM_DOCS % NUM_WORKERS   
    results = []

    with Pool(NUM_WORKERS) as pool:
        for result in pool.map(worker, ndocs):
            results += result
    print(f'{len(results)} documents generated')
    with open(DATA_OUT, "w") as outfile:
        json.dump(results, outfile)   

def worker(ndocs):
    global fake
    result = []

    for _ in range(ndocs):
        uuid = str(uuid4())
        coords = fake.local_latlng(country_code="US", coords_only=True)
        lat = round(float(coords[0]) + random.uniform(-1, 1), 5)  # faker local_latlng generates duplicates.  this is a workaround
        lng = round(float(coords[1]) + random.uniform(-1, 1), 5)
        point_lnglat = f'{lng} {lat}'
        point_wkt = Point(lng, lat).wkt
        dob = fake.date_of_birth(minimum_age=10, maximum_age=90).year
        result.append({"uuid": uuid, "point_lnglat": point_lnglat, "point_wkt": point_wkt, "dob": dob})
    return result

if __name__ == '__main__':
   generate()