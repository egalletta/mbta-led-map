#!/usr/bin/env python3

import argparse
import time

import requests
import serial

import config
import stop_pins
from utils.stops import get_stop_name

# MBTA v3 API key
MBTA_KEY = config.api_key

def main():
    """
    Displays the LED map according to user-specified args.
    """
    # parse arguments for displaying
    parser = argparse.ArgumentParser(description="Options for trains:")
    parser.add_argument('--north', '-n', action='store_true', help="Display trains going northbound")
    parser.add_argument('--south', '-s', action='store_true', help="Display trains going southbound")
    parser.add_argument('--red', '-r', action='store_true', help="Show red line trains")
    parser.add_argument('--green', '-g', action='store_true', help="Show green line trains")
    parser.add_argument('--orange', '-o', action='store_true', help="Show orange line trains")
    parser.add_argument('--blue', '-b', action='store_true', help="Show blue line trains")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable stop output to STDOUT of host.")
    args = parser.parse_args()
    # set up the boards with their respective serial ports and baud rates
    blue_lightboard = serial.Serial('/dev/ttyUSB0', '115200')
    red_lightboard = serial.Serial('/dev/ttyUSB1', '115200')
    green_lightboard = serial.Serial('/dev/ttyUSB2', '115200')
    display = serial.Serial('/dev/ttyUSB3', '115200')
    time.sleep(2)
    write_serial_message("    MBTA LED MAP        Enzo Galletta   ", display)
    time.sleep(2)
    clear_lights(blue_lightboard, red_lightboard, green_lightboard)
    while True:
        if args.south:
            display_lights(blue_lightboard, display, green_lightboard, red_lightboard, 0, "SOUTHBOUND", args)
        if args.north:
            display_lights(blue_lightboard, display, green_lightboard, red_lightboard, 1, "NORTHBOUND", args)


def get_vehicles(line, direction, debugging):
    """ Gets a binary string representation of the current MBTA vehicle positions on the specificed line and direction.
    :param line: a MBTA Subway Line.
    :param direction:  0 for Southbound/Westbound, 1 for Northbound/Eastbound.
    :param debugging: prints stop information to host if true.
    :return: a string consiting of '1' and '0' of vehicle positions, where the position of '1's refer to the LED pin
            for that stop.
    """
    # api-endpoint
    URL = "https://api-v3.mbta.com/vehicles?filter[route]=" + line + "&api_key=" + MBTA_KEY
    vehicles = requests.get(url=URL).json()['data']
    # populating stops
    current_positions, stop_dict = populate_stops(line)
    for vehicle in vehicles:
        if (vehicle['attributes']['direction_id'] == direction):
            try:
                if debugging:
                    print(line + ":    " + get_stop_name(str(vehicle['relationships']['stop']['data']['id'])))
                current_positions[stop_dict[get_stop_name(str(vehicle['relationships']['stop']['data']['id']))]] = True
            except TypeError:
                # in the case of a MBTA vehicle leaving service, that might not have a stop_id
                if debugging:
                    print(line + ":        " + str(vehicle))
    return convert(current_positions)


def display_lights(blue_lightboard, display, green_lightboard, red_lightboard, direction_id, text, args):
    """ Handles updating all serial devices, including LED lights and LCD display
    :param blue_lightboard: Serial object for the blue/orange line lightboard.
    :param display: Serial object for the LCD display.
    :param green_lightboard: Serial object for the green line lightboard.
    :param red_lightboard: Serial object for the red line lightboard.
    :param direction_id: 0 for Southbound/Westbound, 1 for Northbound/Eastbound.
    :param text: Text to display on LCD display.
    :param args: command line args to determine which lines to display.
    """
    write_serial_message("Updating...", display)
    time.sleep(1)
    if args.blue:
        blue_train_positions = get_vehicles(line="Blue", direction=direction_id, debugging=args.debug)
        write_serial_message(message="b" + blue_train_positions, serial_device=blue_lightboard)
    time.sleep(1)
    if args.red:
        red_train_positions = get_vehicles(line="Red", direction=direction_id, debugging=args.debug)
        write_serial_message(message="r" + red_train_positions, serial_device=red_lightboard)
    if args.green:
        green_train_positions = get_vehicles(line="Green-E,Green-B,Green-C,Green-D", direction=direction_id,
                                             debugging=args.debug)
        write_serial_message(message="g" + green_train_positions, serial_device=green_lightboard)
    time.sleep(1.6)
    if args.orange:
        orange_train_positions = get_vehicles(line="Orange", direction=direction_id,
                                              debugging=args.debug)
        write_serial_message(message="o" + orange_train_positions, serial_device=blue_lightboard)
    write_serial_message("Trains " + text, display)
    time.sleep(7)


def clear_lights(blue_lightboard, red_lightboard, green_lightboard):
    """ Clears all leds on the map.
    :param blue_lightboard: Serial object for the blue/orange line lightboard.
    :param red_lightboard: Serial object for the red line lightboard.
    :param green_lightboard: Serial object for the green line lightboard.
    """
    write_serial_message(message="b" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=blue_lightboard)
    time.sleep(1)
    write_serial_message(message="r" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=red_lightboard)
    write_serial_message(message="g" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=green_lightboard)
    time.sleep(1)
    write_serial_message(message="o" + "000000000000000000000000000000000000000000000000000000000000000000000000",
                         serial_device=blue_lightboard)
    time.sleep(1)


def populate_stops(line):
    """ Used in setting up stops for different lines.
    :param line: the line of the stop requested
    :return: current_positions: a list of the same length as the given subway line, filled with False.
    :return: stop_dict: a dictionary with stop names as keys and LED locations as values, specific to specified line.
    :raises: ValueError: If the specified line does not exist.
    """
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
    else:
        raise ValueError('Invalid line')
    return current_positions, stop_dict


def write_serial_message(message, serial_device):
    """ Writes a string message to the specified serial device.
    :param message: The message to send.
    :param serial_device: Serial object to write message to.
    """
    serial_device.write(message.encode())


def convert(list):
    """ Converts a boolean list to a binary-string list.
    :param list: The boolean list to convert
    :return: a binary string.
    """
    result = ""
    for item in list:
        if item is True:
            result = result + "1"
        else:
            result = result + "0"
    return result


if __name__ == '__main__':
    main()
