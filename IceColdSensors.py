#This is very modified version of the script available here: https://medium.com/initial-state/how-to-build-a-raspberry-pi-refrigerator-freezer-monitor-f7a91075c2fd


# Import necessary libraries
import time
import smbus2
import bme280
from ISStreamer.Streamer import Streamer
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# User Settings - Customize these variables according to your needs
SENSOR_LOCATION_NAME_1 = "Freezer"  # Name for the first sensor location
SENSOR_LOCATION_NAME_2 = "Fridge"   # Name for the second sensor location
BUCKET_NAME = "YOUR-BUCKET-NAME-HERE"  # Name of the Initial State bucket
BUCKET_KEY = "YOUR-BUCKET-KEY-HERE"  # Key for the Initial State bucket
ACCESS_KEY = "YOUR KEY HERE"  # Your Initial State access key
MINUTES_BETWEEN_READS = 5  # Time interval between sensor readings in minutes
SLACK_API_TOKEN = "YOUR-SLACK-API-TOKEN-HERE"  # Replace this with your Slack API token

slack_client = WebClient(token=SLACK_API_TOKEN)  # Create a Slack WebClient instance

# Counter variables for temperature checks
fridge_above_40_count = 0
freezer_above_17_count = 0
THRESHOLD_COUNT = 4  # Number of consecutive MINUTES_BETWEEN_READS intervals before sending an alert


# BME280 settings
port = 1  # Raspberry Pi's I2C port number

# Address for Freezer (BME280 sensor)
address_1 = 0x77  # I2C address of the first sensor
bus_1 = smbus2.SMBus(port)  # Create an I2C bus object
calibration_params_1 = bme280.load_calibration_params(bus_1, address_1)  # Load calibration parameters

# Address for Fridge (BME280 sensor)
address_2 = 0x76  # I2C address of the second sensor
bus_2 = smbus2.SMBus(port)  # Create another I2C bus object
calibration_params_2 = bme280.load_calibration_params(bus_2, address_2)  # Load calibration parameters

# Initialize the Initial State streamer objects for each sensor
streamer_1 = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
streamer_2 = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)


# Main loop to continuously read sensor data and perform actions
while True:
    # Get Data from Freezer (Sensor 1)
    bme280data_1 = bme280.sample(bus_1, address_1, calibration_params_1)
    humidity_1 = format(bme280data_1.humidity, ".1f")  # Format humidity value with one decimal place
    temp_c_1 = bme280data_1.temperature
    temp_f_1 = (temp_c_1 * 9/5) + 32  # Convert Celsius to Fahrenheit

    # Log data to Initial State for Sensor 1
    streamer_1.log(SENSOR_LOCATION_NAME_1 + " Temperature(F)", temp_f_1)  # Log temperature data
    streamer_1.log(SENSOR_LOCATION_NAME_1 + " Humidity(%)", humidity_1)  # Log humidity data
    streamer_1.flush()  # Send data to Initial State

    # Check if Freezer is above 17°F for 4 consecutive MINUTES_BETWEEN_READS intervals
    if temp_f_1 > 17:
        freezer_above_17_count += 1
    else:
        freezer_above_17_count = 0

    # Post Temperature to Slack for Freezer if condition is met
    if freezer_above_17_count >= THRESHOLD_COUNT:
        try:
            message_1 = (
                f"ALERT: {SENSOR_LOCATION_NAME_1} Temperature above 17°F for {freezer_above_17_count} consecutive 5 minute intervals\n"
                f"{SENSOR_LOCATION_NAME_1} Temperature: {temp_f_1:.1f}°F\n"
                f"{SENSOR_LOCATION_NAME_1} Humidity: {humidity_1}%"
            )
            slack_client.chat_postMessage(channel="#your-slack-channel", text=message_1)  # Send Slack message
        except SlackApiError as e:
            print(f"Error posting message to Slack: {e}")  # Handle Slack API errors

    # Get Data from Fridge (Sensor 2)
    bme280data_2 = bme280.sample(bus_2, address_2, calibration_params_2)
    humidity_2 = format(bme280data_2.humidity, ".1f")  # Format humidity value with one decimal place
    temp_c_2 = bme280data_2.temperature
    temp_f_2 = (temp_c_2 * 9/5) + 32  # Convert Celsius to Fahrenheit

    # Log data to Initial State for Fridge (Sensor 2)
    streamer_2.log(SENSOR_LOCATION_NAME_2 + " Temperature(F)", temp_f_2)  # Log temperature data
    streamer_2.log(SENSOR_LOCATION_NAME_2 + " Humidity(%)", humidity_2)  # Log humidity data
    streamer_2.flush()  # Send data to Initial State

    # Check if Fridge is above 40°F for 4 consecutive MINUTES_BETWEEN_READS intervals
    if temp_f_2 > 40:
        fridge_above_40_count += 1
    else:
        fridge_above_40_count = 0

    # Post Temperature to Slack for Fridge if condition is met
    if fridge_above_40_count >= THRESHOLD_COUNT:
        try:
            message_2 = (
                f"ALERT: {SENSOR_LOCATION_NAME_2} Temperature above 40°F for {fridge_above_40_count} consecutive 5 minute intervals!\n"
                f"{SENSOR_LOCATION_NAME_2} Temperature: {temp_f_2:.1f}°F\n"
                f"{SENSOR_LOCATION_NAME_2} Humidity: {humidity_2}%"
            )
            slack_client.chat_postMessage(channel="#your-slack-channel", text=message_2)  # Send Slack message
        except SlackApiError as e:
            print(f"Error posting message to Slack: {e}")  # Handle Slack API errors

    # Sleep for the specified interval before the next iteration
    time.sleep(60 * MINUTES_BETWEEN_READS)
