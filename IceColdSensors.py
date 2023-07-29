#This is a modified version of the `freezer_monitor.py` script available in this tutorial: 
#https://medium.com/initial-state/how-to-build-a-raspberry-pi-refrigerator-freezer-monitor-f7a91075c2fd

#ADDED: Dual sensor functionality, Conversion to Fahrenheit, Slack integration with configurable threshold temps and times

# Import necessary libraries
import time  # Time-related functions
import smbus2  # I2C communication library
import bme280  # Library to interface with BME280 sensor
from ISStreamer.Streamer import Streamer  # Library for logging data to Initial State
from slack_sdk import WebClient  # Library for interacting with Slack API
from slack_sdk.errors import SlackApiError  # Error handling for Slack API

# User Settings - Customize these variables according to your needs

# Name for the first sensor location (e.g., "Freezer")
SENSOR_LOCATION_NAME_1 = "Freezer"
# Name for the second sensor location (e.g., "Fridge")
SENSOR_LOCATION_NAME_2 = "Fridge"
# Name of the Initial State bucket
BUCKET_NAME = "YOUR-BUCKET-NAME-HERE"
# Key for the Initial State bucket
BUCKET_KEY = "YOUR-BUCKET-KEY-HERE"
# Your Initial State access key
ACCESS_KEY = "YOUR KEY HERE"
# Time interval between sensor readings in minutes
MINUTES_BETWEEN_READS = 5
# Replace this with your Slack API token
SLACK_API_TOKEN = "YOUR-SLACK-API-TOKEN-HERE"
# Replace this with your Slack channel name
SLACK_CHANNEL = "YOUR-CHANNEL-NAME-HERE"
# Replace the following list with the Slack usernames you want to tag
SLACK_USERS_TO_TAG = ["@username1", "@username2", "@username3"] #Remove everything between brackets if no users are to be tagged.
# Threshold temperature for the Freezer
FREEZER_THRESHOLD_TEMP = 17
# Threshold temperature for the Fridge
FRIDGE_THRESHOLD_TEMP = 40
# Number of consecutive MINUTES_BETWEEN_READS intervals before sending an alert
THRESHOLD_COUNT = 4


# Counter variables for temperature checks
FRIDGE_ABOVE_THRESHOLD_COUNT = 0
FREEZER_ABOVE_THRESHOLD_COUNT = 0

# Variables to store alert messages
freezer_alert_message = ""
fridge_alert_message = ""

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
    temp_f_1 = (temp_c_1 * 9 / 5) + 32  # Convert Celsius to Fahrenheit

    # Log data to Initial State for Sensor 1
    streamer_1.log(SENSOR_LOCATION_NAME_1 + " Temperature(F)", temp_f_1)  # Log temperature data
    streamer_1.log(SENSOR_LOCATION_NAME_1 + " Humidity(%)", humidity_1)  # Log humidity data
    streamer_1.flush()  # Send data to Initial State

    # Get Data from Fridge (Sensor 2)
    bme280data_2 = bme280.sample(bus_2, address_2, calibration_params_2)
    humidity_2 = format(bme280data_2.humidity, ".1f")  # Format humidity value with one decimal place
    temp_c_2 = bme280data_2.temperature
    temp_f_2 = (temp_c_2 * 9 / 5) + 32  # Convert Celsius to Fahrenheit

    # Log data to Initial State for Fridge (Sensor 2)
    streamer_2.log(SENSOR_LOCATION_NAME_2 + " Temperature(F)", temp_f_2)  # Log temperature data
    streamer_2.log(SENSOR_LOCATION_NAME_2 + " Humidity(%)", humidity_2)  # Log humidity data
    streamer_2.flush()  # Send data to Initial State

    # Check if Freezer is above THRESHOLD_TEMP for THRESHOLD_COUNT consecutive MINUTES_BETWEEN_READS intervals
    if temp_f_1 > FREEZER_THRESHOLD_TEMP:
        FREEZER_ABOVE_THRESHOLD_COUNT += 1
    else:
        FREEZER_ABOVE_THRESHOLD_COUNT = 0

    # Post Temperature to Slack for Freezer if condition is met
    if FREEZER_ABOVE_THRESHOLD_COUNT >= THRESHOLD_COUNT:
        freezer_alert_message = (
            f"ALERT: {SENSOR_LOCATION_NAME_1} Temperature above {FREEZER_THRESHOLD_TEMP} for {FREEZER_ABOVE_THRESHOLD_COUNT} consecutive {THRESHOLD_COUNT} minute intervals\n"
            f"{SENSOR_LOCATION_NAME_1} Temperature: {temp_f_1:.1f}°F\n"
            f"{SENSOR_LOCATION_NAME_1} Humidity: {humidity_1}%\n"
        )

    # Check if Fridge is above FRIDGE_THRESHOLD_TEMP for THRESHOLD_COUNT consecutive MINUTES_BETWEEN_READS intervals
    if temp_f_2 > FRIDGE_THRESHOLD_TEMP:
        FRIDGE_ABOVE_THRESHOLD_COUNT += 1
    else:
        FRIDGE_ABOVE_THRESHOLD_COUNT = 0

    # Post Temperature to Slack for Fridge if condition is met
    if FRIDGE_ABOVE_THRESHOLD_COUNT >= THRESHOLD_COUNT:
        fridge_alert_message = (
            f"ALERT: {SENSOR_LOCATION_NAME_2} Temperature above {FRIDGE_THRESHOLD_TEMP} for {FRIDGE_ABOVE_THRESHOLD_COUNT} consecutive {THRESHOLD_COUNT} minute intervals\n"
            f"{SENSOR_LOCATION_NAME_2} Temperature: {temp_f_2:.1f}°F\n"
            f"{SENSOR_LOCATION_NAME_2} Humidity: {humidity_2}%\n"
        )

    # Send combined Slack message if any of the alerts are triggered
    if freezer_alert_message or fridge_alert_message:
        # Create a Slack WebClient instance
        slack_client = WebClient(token=SLACK_API_TOKEN)
        try:
            combined_message = freezer_alert_message + fridge_alert_message

            # Prepare the list of user IDs to tag in the message
            tagged_users = " ".join(SLACK_USERS_TO_TAG)

            # Add the tagged users to the beginning of the message
            combined_message_with_tags = f"{tagged_users} {combined_message}"

            slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=combined_message_with_tags)  # Send Slack message
        except SlackApiError as e:
            print(f"Error posting message to Slack: {e}")  # Handle Slack API errors

        # Reset alert messages
        freezer_alert_message = ""
        fridge_alert_message = ""

    # Sleep for the specified interval before the next iteration
    time.sleep(60 * MINUTES_BETWEEN_READS)
