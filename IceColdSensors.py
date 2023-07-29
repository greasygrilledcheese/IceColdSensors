# Import necessary libraries
import time  # Time-related functions
import smbus2  # I2C communication library
import bme280  # Library to interface with BME280 sensor
from ISStreamer.Streamer import Streamer  # Library for logging data to Initial State
from slack_sdk import WebClient  # Library for interacting with Slack API
from slack_sdk.errors import SlackApiError  # Error handling for Slack API
import configparser

# Function to read settings from the .conf file
def read_settings_from_conf(conf_file):
    config = configparser.ConfigParser()
    config.read(conf_file)

    settings = {}
    settings['SENSOR_LOCATION_NAME_1'] = config.get('General', 'SENSOR_LOCATION_NAME_1')
    settings['SENSOR_LOCATION_NAME_2'] = config.get('General', 'SENSOR_LOCATION_NAME_2')
    settings['BUCKET_NAME'] = config.get('General', 'BUCKET_NAME')
    settings['BUCKET_KEY'] = config.get('General', 'BUCKET_KEY')
    settings['ACCESS_KEY'] = config.get('General', 'ACCESS_KEY')
    settings['MINUTES_BETWEEN_READS'] = config.getint('General', 'MINUTES_BETWEEN_READS')
    settings['SLACK_API_TOKEN'] = config.get('General', 'SLACK_API_TOKEN')
    settings['SLACK_CHANNEL'] = config.get('General', 'SLACK_CHANNEL')
    settings['SLACK_USERS_TO_TAG'] = config.get('General', 'SLACK_USERS_TO_TAG').split()
    settings['FREEZER_THRESHOLD_TEMP'] = config.getfloat('General', 'FREEZER_THRESHOLD_TEMP')
    settings['FRIDGE_THRESHOLD_TEMP'] = config.getfloat('General', 'FRIDGE_THRESHOLD_TEMP')
    settings['THRESHOLD_COUNT'] = config.getint('General', 'THRESHOLD_COUNT')

    return settings

# Read the  from the .conf file
settings = read_settings_from_conf('IceColdSettings.conf')

# User Settings - Customize these variables according to your needs
SENSOR_LOCATION_NAME_1 = settings['SENSOR_LOCATION_NAME_1']
SENSOR_LOCATION_NAME_2 = settings['SENSOR_LOCATION_NAME_2']
BUCKET_NAME = settings['BUCKET_NAME']
BUCKET_KEY = settings['BUCKET_KEY']
ACCESS_KEY = settings['ACCESS_KEY']
MINUTES_BETWEEN_READS = settings['MINUTES_BETWEEN_READS']
SLACK_API_TOKEN = settings['SLACK_API_TOKEN']
SLACK_CHANNEL = settings['SLACK_CHANNEL']
SLACK_USERS_TO_TAG = settings['SLACK_USERS_TO_TAG']
FREEZER_THRESHOLD_TEMP = settings['FREEZER_THRESHOLD_TEMP']
FRIDGE_THRESHOLD_TEMP = settings['FRIDGE_THRESHOLD_TEMP']
THRESHOLD_COUNT = settings['THRESHOLD_COUNT']

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
