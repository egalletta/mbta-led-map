import time

import requests
import serial

import config
import stops
from utils.stops import get_stop_name

MBTA_KEY = config.api_key

def populate_stops(line):
    if (line == "Blue"):
        current_positions = [False] * 12
        stop_dict = stops.blue
    elif (line == "Orange"):
        current_positions = [False] * 20
        stop_dict = stops.orange
    elif (line == "Red"):
        current_positions = [False] * 22
        stop_dict = stops.red
    elif ("Green" in line):
        current_positions = [False] * 72
        stop_dict = stops.green
    return current_positions, stop_dict


def write_serial_message(message, serial_device):
    serial_device.write(message.encode())


def convert(list):
    result = ""
    for item in list:
        if item is True:
            result = result + "1"
        else:
            result = result + "0"
    return result

def get_vehicles(line, direction):
    # api-endpoint
    URL = "https://api-v3.mbta.com/vehicles?filter[route]=" + line + "&api_key=" + MBTA_KEY
    vehicles = requests.get(url=URL).json()['data']
    #populating stops
    current_positions, stop_dict = populate_stops(line)
    for vehicle in vehicles:
        if (vehicle['attributes']['direction_id'] == direction):
            current_positions[stop_dict[get_stop_name(str(vehicle['relationships']['stop']['data']['id']))]] = True
    return convert(current_positions)


def main():
    # set up the boards with their respective serial ports
    blue_lightboard = serial.Serial('/dev/ttyUSB0', '115200')
    red_lightboard = serial.Serial('/dev/ttyUSB1', '115200')
    green_lightboard = serial.Serial('/dev/ttyUSB2', '115200')
    display = serial.Serial('/dev/ttyUSB3', '115200')
    while True:
        # get southbound trains
        write_serial_message("Trains NORTHBOUND   Updating...", display)
        blue_train_positions = get_vehicles(line="Blue", direction=0)
        orange_train_positions = get_vehicles(line="Orange", direction=0)
        red_train_positions = get_vehicles(line="Red", direction=0)
        green_train_positions = get_vehicles(line="Green-E,Green-B,Green-C,Green-D", direction=0)
        clear_lights(blue_lightboard, red_lightboard, green_lightboard)
        time.sleep(0.6)
        write_serial_message(message="b" + blue_train_positions, serial_device=blue_lightboard)
        time.sleep(0.6)
        write_serial_message(message="r" + red_train_positions, serial_device=red_lightboard)
        write_serial_message(message="g" + green_train_positions, serial_device=green_lightboard)
        time.sleep(0.6)
        write_serial_message(message="o" + orange_train_positions, serial_device=blue_lightboard)
        write_serial_message("Trains SOUTHBOUND", display)
        time.sleep(8)
        # get northbound trains
        write_serial_message("Trains SOUTHBOUND   Updating...", display)
        blue_train_positions = get_vehicles(line="Blue", direction=1)
        orange_train_positions = get_vehicles(line="Orange", direction=1)
        red_train_positions = get_vehicles(line="Red", direction=1)
        green_train_positions = get_vehicles(line="Green-E,Green-B,Green-C,Green-D", direction=1)
        clear_lights(blue_lightboard, red_lightboard)
        time.sleep(0.6)
        write_serial_message(message="b" + blue_train_positions, serial_device=blue_lightboard)
        time.sleep(.6)
        write_serial_message(message="r" + red_train_positions, serial_device=red_lightboard)
        write_serial_message(message="g" + green_train_positions, serial_device=green_lightboard)
        time.sleep(.6)
        write_serial_message(message="o" + orange_train_positions, serial_device=blue_lightboard)
        write_serial_message("Trains NORTHBOUND", display)
        time.sleep(8)


def clear_lights(blue_lightboard, red_lightboard, green_lightboard):
    write_serial_message(message="b" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=blue_lightboard)
    time.sleep(0.6)
    write_serial_message(message="r" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=red_lightboard)
    write_serial_message(message="g" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=green_lightboard)
    time.sleep(0.6)
    write_serial_message(message="o" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=blue_lightboard)
    time.sleep(0.6)


if __name__ == '__main__':
    main()
