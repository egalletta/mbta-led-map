import mbta_controller as mbta
import serial
import time

def main():
    blue_lightboard = serial.Serial('/dev/ttyUSB0', '115200')
    red_lightboard = serial.Serial('/dev/ttyUSB1', '115200')
    green_lightboard = serial.Serial('/dev/ttyUSB2', '115200')
    display = serial.Serial('/dev/ttyUSB3', '115200')
    time.sleep(2)
    mbta.write_serial_message("Hello Word!", display)
    time.sleep(2)
    mbta.write_serial_message("b111111111111111111111111111111111111111111111111111111111111111111111111",
                              blue_lightboard)
    time.sleep(2)
    mbta.write_serial_message("o111111111111111111111111111111111111111111111111111111111111111111111111",
                              blue_lightboard)
    time.sleep(2)
    mbta.write_serial_message("r111111111111111111111111111111111111111111111111111111111111111111111111",
                              red_lightboard)
    time.sleep(2)
    mbta.write_serial_message("b111111111111111111111111111111111111111111111111111111111111111111111111",
                              green_lightboard)

if __name__ == '__main__':
    main()

