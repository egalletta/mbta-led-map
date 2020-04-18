import json
import pickle
from os import path

import requests

def main():
    URL = "https://api-v3.mbta.com/stops"
    stops = requests.get(URL).json()['data']
    stops_optimized = dict()
    for stop in stops:
        stops_optimized[stop['id']] = stop['attributes']['name']
    with open("stops.pickle", "wb") as file:
         pickle.dump(stops_optimized, file, protocol=pickle.HIGHEST_PROTOCOL)

def get_stop_name(id):
    if not path.exists("stops.pickle"):
        main()
    with open("stops.pickle", "rb") as file:
        stops = pickle.load(file)
        return stops.get(id)

if __name__ == '__main__':
    main()
