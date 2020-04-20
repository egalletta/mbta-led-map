import argparse
import time

import requests
import serial

import config
import stop_pins
from utils.stops import get_stop_name

MBTA_KEY = config.api_key

def populate_stops(line):
    if (line == "Blue"):
        current_positions = [False] * 12
        stop_dict = stop_pins.blue
    elif (line == "Orange"):
        current_positions = [False] * 20
        stop_dict = stop_pins.orange
    elif (line == "Red"):
        current_positions = [False] * 22
        stop_dict = stop_pins.red
    elif ("Green" in line):
        current_positions = [False] * 75
        stop_dict = stop_pins.green
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
            try:
                 print(get_stop_name(str(vehicle['relationships']['stop']['data']['id'])))
                 current_positions[stop_dict[get_stop_name(str(vehicle['relationships']['stop']['data']['id']))]] = True
            except TypeError:
                 print(vehicle)

    return convert(current_positions)


def main():
    # parse arguments for displaying
    parser = argparse.ArgumentParser(description="Options for trains:")
    parser.add_argument('--north', '-n', action='store_true', help="Display trains going northbound")
    parser.add_argument('--south', '-s', action='store_true', help="Display trains going southbound")
    parser.add_argument('--red', '-r', action='store_true', help="Show red line trains")
    parser.add_argument('--green', '-g', action='store_true', help="Show green line trains")
    parser.add_argument('--orange', '-o', action='store_true', help="Show orange line trains")
    parser.add_argument('--blue', '-b', action='store_true', help="Show blue line trains")
    args = parser.parse_args()
    # set up the boards with their respective serial ports
    blue_lightboard = serial.Serial('/dev/ttyUSB0', '115200')
    red_lightboard = serial.Serial('/dev/ttyUSB1', '115200')
    green_lightboard = serial.Serial('/dev/ttyUSB2', '115200')
    display = serial.Serial('/dev/ttyUSB3', '115200')
    while True:
        if args.south:
            display_lights(blue_lightboard, display, green_lightboard, red_lightboard, 0, "SOUTHBOUND", args)
        if args.north:
            display_lights(blue_lightboard, display, green_lightboard, red_lightboard, 1, "NORTHBOUND", args)


def display_lights(blue_lightboard, display, green_lightboard, red_lightboard, direction_id, text, args):
    # get southbound trains
    write_serial_message("Updating...", display)
    time.sleep(0.6)
    if args.blue:
        blue_train_positions = get_vehicles(line="Blue", direction=direction_id)
        write_serial_message(message="b" + blue_train_positions, serial_device=blue_lightboard)
    time.sleep(0.6)
    if args.red:
        red_train_positions = get_vehicles(line="Red", direction=direction_id)
        write_serial_message(message="r" + red_train_positions, serial_device=red_lightboard)
    if args.green:
        green_train_positions = get_vehicles(line="Green-E,Green-B,Green-C,Green-D", direction=direction_id)
        write_serial_message(message="g" + green_train_positions, serial_device=green_lightboard)
    time.sleep(0.6)
    if args.orange:
        orange_train_positions = get_vehicles(line="Orange", direction=direction_id)
        write_serial_message(message="o" + orange_train_positions, serial_device=blue_lightboard)
    write_serial_message("Trains " + text, display)
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
