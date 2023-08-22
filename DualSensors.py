# Import necessary libraries
import time
import smbus2
import bme280
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import configparser
from Adafruit_IO import Client

# Define log file locations
LOG_FILE = "sensor_readings.log"
ERROR_LOG_FILE = "error_log.log"

# Function to read settings from the configuration file
def read_settings_from_conf(conf_file):
    config = configparser.ConfigParser()
    config.read(conf_file)
    settings = {}
    for key in ['SENSOR_LOCATION_NAME', 'MINUTES_BETWEEN_READS', 'SLACK_API_TOKEN',
                'SLACK_CHANNEL', 'SLACK_USERS_TO_TAG', 'SENSOR_THRESHOLD_TEMP',
                'THRESHOLD_COUNT', 'ADAFRUIT_IO_USERNAME', 'ADAFRUIT_IO_KEY']:
        try:
            if key in ['SENSOR_THRESHOLD_TEMP']:
                settings[key] = config.getfloat('General', key)
            elif key in ['MINUTES_BETWEEN_READS', 'THRESHOLD_COUNT']:
                settings[key] = config.getint('General', key)
            elif key == 'SLACK_USERS_TO_TAG':
                settings[key] = config.get('General', key).split()
            else:
                settings[key] = config.get('General', key)
        except configparser.NoOptionError:
            log_error(f"Missing {key} in configuration file.")
            raise
    return settings

# Function to log errors
def log_error(message):
    with open(ERROR_LOG_FILE, 'a') as file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - ERROR: {message}\n")

# Function to log sensor readings to a file
def log_to_file(sensor_name, temperature, humidity):
    with open(LOG_FILE, 'a') as file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - {sensor_name} - Temperature: {temperature}°F, Humidity: {humidity}%\n")

# Read settings from the configuration file
settings = read_settings_from_conf('DualSensorSettings.conf')

# Extract sensor and configuration data
SENSOR_LOCATION_NAME = settings['SENSOR_LOCATION_NAME']
MINUTES_BETWEEN_READS = settings['MINUTES_BETWEEN_READS']
SLACK_API_TOKEN = settings['SLACK_API_TOKEN']
SLACK_CHANNEL = settings['SLACK_CHANNEL']
SLACK_USERS_TO_TAG = settings['SLACK_USERS_TO_TAG']
SENSOR_THRESHOLD_TEMP = settings['SENSOR_THRESHOLD_TEMP']
THRESHOLD_COUNT = settings['THRESHOLD_COUNT']
ADAFRUIT_IO_USERNAME = settings['ADAFRUIT_IO_USERNAME']
ADAFRUIT_IO_KEY = settings['ADAFRUIT_IO_KEY']

# Initialize threshold counters and alert flags
SENSOR_ABOVE_THRESHOLD_COUNT = [0, 0]
SENSOR_ALERT_SENT = [False, False]

# Initialize BME280 sensors
port = 1
address_1 = 0x77
address_2 = 0x76
bus_1 = smbus2.SMBus(port)
calibration_params_1 = bme280.load_calibration_params(bus_1, address_1)
calibration_params_2 = bme280.load_calibration_params(bus_1, address_2)

# Initialize Slack client
slack_client = WebClient(token=SLACK_API_TOKEN)

# Initialize Adafruit IO client
adafruit_io_client = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Main loop for reading data, logging, and sending alerts
while True:
    sensor_alert_messages = ["", ""]
    for sensor_index, (address, calibration_params) in enumerate([(address_1, calibration_params_1), (address_2, calibration_params_2)]):
        try:
            # Read data from the BME280 sensors
            bme280data = bme280.sample(bus_1, address, calibration_params)
            humidity = format(bme280data.humidity, ".1f")
            temp_c = bme280data.temperature
            temp_f = (temp_c * 9 / 5) + 32

            # Log to file
            log_to_file(f"{SENSOR_LOCATION_NAME} {sensor_index + 1}", temp_f, humidity)

            # Send temperature and humidity to Adafruit IO
            adafruit_io_client.send(f'temperature_{sensor_index + 1}', temp_f)
            adafruit_io_client.send(f'humidity_{sensor_index + 1}', humidity)

            # Check thresholds and prepare alerts for the sensor
            if temp_f > SENSOR_THRESHOLD_TEMP:
                SENSOR_ABOVE_THRESHOLD_COUNT[sensor_index] += 1
                if SENSOR_ABOVE_THRESHOLD_COUNT[sensor_index] >= THRESHOLD_COUNT and not SENSOR_ALERT_SENT[sensor_index]:
                    sensor_alert_messages[sensor_index] = (
                        f"ALERT: {SENSOR_LOCATION_NAME} {sensor_index + 1} Temperature above {SENSOR_THRESHOLD_TEMP}°F\n"
                        f"{SENSOR_LOCATION_NAME} {sensor_index + 1} Temperature: {temp_f:.1f}°F\n"
                        f"{SENSOR_LOCATION_NAME} {sensor_index + 1} Humidity: {humidity}%\n"
                    )
                    SENSOR_ALERT_SENT[sensor_index] = True
            elif temp_f <= SENSOR_THRESHOLD_TEMP and SENSOR_ALERT_SENT[sensor_index]:
                sensor_alert_messages[sensor_index] = (
                    f"NOTICE: {SENSOR_LOCATION_NAME} {sensor_index + 1} Temperature is now back within range at {temp_f:.1f}°F\n"
                )
                SENSOR_ALERT_SENT[sensor_index] = False
                SENSOR_ABOVE_THRESHOLD_COUNT[sensor_index] = 0

        except Exception as e:
            log_error(f"Error reading or logging data for sensor {sensor_index + 1}: {e}")

    # Send alert messages to Slack
    for sensor_alert_message in sensor_alert_messages:
        if sensor_alert_message:
            try:
                tagged_users = " ".join(SLACK_USERS_TO_TAG)
                combined_message_with_tags = f"{tagged_users} {sensor_alert_message}"
                slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=combined_message_with_tags)
            except SlackApiError as e:
                log_error(f"Error posting message to Slack: {e}")

    time.sleep(60 * MINUTES_BETWEEN_READS)
