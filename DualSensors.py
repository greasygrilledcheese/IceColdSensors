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
    keys = [
        'SENSOR_LOCATION_NAME_1', 'SENSOR_LOCATION_NAME_2', 'MINUTES_BETWEEN_READS',
        'SLACK_API_TOKEN', 'SLACK_CHANNEL', 'SLACK_USERS_TO_TAG',
        'SENSOR_THRESHOLD_TEMP_1', 'SENSOR_THRESHOLD_TEMP_2',
        'THRESHOLD_COUNT',
        'ADAFRUIT_IO_USERNAME', 'ADAFRUIT_IO_KEY', 'ADAFRUIT_IO_GROUP_NAME',
        'ADAFRUIT_IO_TEMP_FEED_1', 'ADAFRUIT_IO_HUMIDITY_FEED_1',
        'ADAFRUIT_IO_TEMP_FEED_2', 'ADAFRUIT_IO_HUMIDITY_FEED_2'
    ]
    for key in keys:
        try:
            if key in ['SENSOR_THRESHOLD_TEMP_1', 'SENSOR_THRESHOLD_TEMP_2']:
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

# Function to log sensor readings
def log_to_file(sensor_name, temperature, humidity):
    with open(LOG_FILE, 'a') as file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - {sensor_name} - Temperature: {temperature}°F, Humidity: {humidity}%\n")

# Read settings from the configuration file
settings = read_settings_from_conf('DualSensorSettings.conf')

# Extract settings into global variables
for key, value in settings.items():
    globals()[key] = value

# Initialize threshold counters and alert flags
SENSOR_ABOVE_THRESHOLD_COUNT = [0, 0]
SENSOR_ALERT_SENT = [False, False]

# Initialize BME280 sensors
port = 1
address_1, address_2 = 0x77, 0x76
bus_1 = smbus2.SMBus(port)
calibration_params_1 = bme280.load_calibration_params(bus_1, address_1)
calibration_params_2 = bme280.load_calibration_params(bus_1, address_2)

# Initialize Slack client
slack_client = WebClient(token=SLACK_API_TOKEN)

# Initialize Adafruit IO client
adafruit_io_client = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Main loop
while True:
    sensor_alert_messages = ["", ""]
    for i, (address, calibration_params, sensor_location_name, threshold_temp, temp_feed, humid_feed) in enumerate([
        (address_1, calibration_params_1, SENSOR_LOCATION_NAME_1, SENSOR_THRESHOLD_TEMP_1, ADAFRUIT_IO_TEMP_FEED_1, ADAFRUIT_IO_HUMIDITY_FEED_1),
        (address_2, calibration_params_2, SENSOR_LOCATION_NAME_2, SENSOR_THRESHOLD_TEMP_2, ADAFRUIT_IO_TEMP_FEED_2, ADAFRUIT_IO_HUMIDITY_FEED_2)
    ]):
        try:
            bme280data = bme280.sample(bus_1, address, calibration_params)
            humidity = format(bme280data.humidity, ".1f")
            temp_c = bme280data.temperature
            temp_f = (temp_c * 9 / 5) + 32
            log_to_file(sensor_location_name, temp_f, humidity)
            
            # Send to Adafruit IO
            adafruit_io_client.send(f"{ADAFRUIT_IO_GROUP_NAME}.{temp_feed}", temp_f)
            adafruit_io_client.send(f"{ADAFRUIT_IO_GROUP_NAME}.{humid_feed}", humidity)
            
            if temp_f > threshold_temp:
                SENSOR_ABOVE_THRESHOLD_COUNT[i] += 1
                if SENSOR_ABOVE_THRESHOLD_COUNT[i] >= THRESHOLD_COUNT and not SENSOR_ALERT_SENT[i]:
                    sensor_alert_messages[i] = f"ALERT: {sensor_location_name} Temperature above {threshold_temp}°F\n"
                    SENSOR_ALERT_SENT[i] = True
            elif temp_f <= threshold_temp and SENSOR_ALERT_SENT[i]:
                sensor_alert_messages[i] = f"NOTICE: {sensor_location_name} Temperature is now back within range at {temp_f:.1f}°F\n"
                SENSOR_ALERT_SENT[i] = False
                SENSOR_ABOVE_THRESHOLD_COUNT[i] = 0
        except Exception as e:
            log_error(f"Error reading or logging data for sensor {sensor_location_name}: {e}")

    for sensor_alert_message in sensor_alert_messages:
        if sensor_alert_message:
            try:
                tagged_users = " ".join(SLACK_USERS_TO_TAG)
                combined_message_with_tags = f"{tagged_users} {sensor_alert_message}"
                slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=combined_message_with_tags)
            except SlackApiError as e:
                log_error(f"Error posting message to Slack: {e}")

    time.sleep(60 * MINUTES_BETWEEN_READS)
