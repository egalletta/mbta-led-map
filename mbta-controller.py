import time
import requests
import serial
import config

MBTA_KEY = config.api_key

blue_stops = {
"Bowdoin" : 8,
"Government Center" : 9,
"State" : 10,
"Aquarium" : 11,
"Maverick" : 0,
"Airport" : 1,
"Wood Island" : 2,
"Orient Heights" : 3,
"Suffolk Downs" : 4,
"Beachmont" : 5,
"Revere Beach" : 6,
"Wonderland" : 7
}

orange_stops = {
"Forest Hills" : 16,
"Green Street" : 17,
"Stony Brook" : 18,
"Jackson Square" : 19,
"Roxbury Crossing" : 8,
"Ruggles" : 9,
"Massachusetts Avenue" : 10,
"Back Bay" : 11,
"Tufts Medical Center" : 12,
"Chinatown" : 13,
"Downtown Crossing" : 14,
"State" : 15,
"Haymarket" : 0,
"North Station" : 1,
"Community College" : 2,
"Sullivan Square" : 3,
"Assembly" : 4,
"Wellington" : 5,
"Malden Center" : 6,
"Oak Grove" : 7
}

red_stops = {
"Alewife" : 10,
"Davis" : 9,
"Porter" : 8,
"Harvard" : 21,
"Central" : 20,
"Kendall/MIT" : 19,
"Charles/MGH" : 18,
"Park Street" : 17,
"Downtown Crossing" : 16,
"South Station" : 7,
"Broadway" : 6,
"Andrew" : 5,
"JFK/UMass" : 4,
"Savin Hill" : 14,
"Fields Corner" : 13,
"Shawmut" : 12,
"Ashmont" : 11,
"North Quincy" : 3,
"Wollaston" : 2,
"Quincy Center" : 1,
"Quincy Adams" : 0,
"Braintree" : 15
}

def get_vehicles(line, direction):
    stop_dict = {}
    # api-endpoint
    URL = "https://api-v3.mbta.com/vehicles?filter[route]=" + line + "&api_key=" + MBTA_KEY
    # headers = {'x-api-key': 'vMcznyeweEOs4AcHomvwpw'}
    # sending get request and saving the response as response object
    r = requests.get(url=URL)

    # extracting data in json format
    mbta_data = r.json()
    print(mbta_data)
    vehicles = mbta_data['data']
    #populating stops
    current_positions, stop_dict = populate_stops(line)
    for vehicle in vehicles:
        if (vehicle['attributes']['direction_id'] == direction):
            place_URL = "https://api-v3.mbta.com/stops/" + str(vehicle['relationships']['stop']['data']['id']) + "&api_key=" + MBTA_KEY
            place_req = requests.get(place_URL)
            place_data = place_req.json()
            place_data = place_data['data']
            print(place_data['attributes']['name'])
            current_positions[stop_dict[place_data['attributes']['name']]] = True
    return convert(current_positions)


def populate_stops(line):
    if (line == "Blue"):
        current_positions = [False] * 12
        stop_dict = blue_stops
    elif (line == "Orange"):
        current_positions = [False] * 20
        stop_dict = orange_stops
    elif (line == "Red"):
        current_positions = [False] * 22
        stop_dict = red_stops
    return current_positions, stop_dict


def write_serial_message(message, serial_device):
    serial_device.write(message.encode())


def convert(list):
    res = ""
    for item in list:
        if item is True:
            res = res + "1"
        else:
            res = res + "0"
    return res

blue_lightboard = serial.Serial('/dev/ttyUSB0', '9600')
red_lightboard = serial.Serial('/dev/ttyUSB1', '9600')
display = serial.Serial('/dev/ttyUSB2', '9600')
write_serial_message(message="b" + "00000000000000000000000000000000000000000000000000", serial_device=blue_lightboard)
time.sleep(1)
write_serial_message(message="r" + "000000000000000000000000000000000000000000000000000", serial_device=red_lightboard)
time.sleep(1)
write_serial_message(message="o" + "000000000000000000000000000000000000000000000000000", serial_device=blue_lightboard)
#lcd_display = serial.Serial('/dev/ttyUSB1', '9600')
time.sleep(2)
while True:
    write_serial_message("Updating...", display)
    blue_train_positions = get_vehicles(line="Blue", direction=0)
    orange_train_positions = get_vehicles(line="Orange", direction=0)
    red_train_positions = get_vehicles(line="Red", direction=0)
    time.sleep(2)
    write_serial_message(message="b" + blue_train_positions, serial_device=blue_lightboard)
    time.sleep(1)
    write_serial_message(message="r" + red_train_positions, serial_device=red_lightboard)
    time.sleep(2)
    write_serial_message(message="o" + orange_train_positions, serial_device=blue_lightboard)
    write_serial_message("Trains SOUTHBOUND", display)
    print(orange_train_positions)
    #write_serial_message(message="Blue Line - Bowdoin", serial_device=lcd_display)
    time.sleep(15)
    write_serial_message("Updating...", display)
    blue_train_positions = get_vehicles(line="Blue", direction=1)
    orange_train_positions = get_vehicles(line="Orange", direction=1)
    red_train_positions = get_vehicles(line="Red", direction=1)
    time.sleep(2)
    write_serial_message(message="b" + blue_train_positions, serial_device=blue_lightboard)
    time.sleep(1)
    write_serial_message(message="r" + red_train_positions, serial_device=red_lightboard)
    time.sleep(2)
    write_serial_message(message="o" + orange_train_positions, serial_device=blue_lightboard)
    write_serial_message("Trains NORTHBOUND", display)
    print(orange_train_positions)
    time.sleep(15)

