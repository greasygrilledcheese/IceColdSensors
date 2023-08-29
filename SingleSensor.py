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

def read_settings_from_conf(conf_file):
    config = configparser.ConfigParser()
    config.read(conf_file)
    settings = {}
    keys = ['SENSOR_LOCATION_NAME', 'MINUTES_BETWEEN_READS', 'SLACK_API_TOKEN',
            'SLACK_CHANNEL', 'SLACK_USERS_TO_TAG', 'SENSOR_THRESHOLD_TEMP',
            'THRESHOLD_COUNT', 'ADAFRUIT_IO_USERNAME', 'ADAFRUIT_IO_KEY',
            'ADAFRUIT_IO_GROUP_NAME', 'ADAFRUIT_IO_TEMP_FEED', 'ADAFRUIT_IO_HUMIDITY_FEED']
    for key in keys:
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

def log_error(message):
    with open(ERROR_LOG_FILE, 'a') as file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - ERROR: {message}\n")

def log_to_file(sensor_name, temperature, humidity):
    with open(LOG_FILE, 'a') as file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - {sensor_name} - Temperature: {temperature}°F, Humidity: {humidity}%\n")

# Read settings from the configuration file
settings = read_settings_from_conf('SingleSensorSettings.conf')

# Extract settings
for key, value in settings.items():
    globals()[key] = value

SENSOR_ABOVE_THRESHOLD_COUNT = 0
SENSOR_ALERT_SENT = False

port = 1
address_1 = 0x77
bus_1 = smbus2.SMBus(port)
calibration_params_1 = bme280.load_calibration_params(bus_1, address_1)

slack_client = WebClient(token=SLACK_API_TOKEN)
adafruit_io_client = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

sensor_alert_message = ""

while True:
    try:
        bme280data_1 = bme280.sample(bus_1, address_1, calibration_params_1)
        humidity_1 = format(bme280data_1.humidity, ".1f")
        temp_c_1 = bme280data_1.temperature
        temp_f_1 = (temp_c_1 * 9 / 5) + 32
        log_to_file(SENSOR_LOCATION_NAME, temp_f_1, humidity_1)

        # Modified lines to use settings from config file
        adafruit_io_client.send(f"{ADAFRUIT_IO_GROUP_NAME}.{ADAFRUIT_IO_TEMP_FEED}", temp_f_1)
        adafruit_io_client.send(f"{ADAFRUIT_IO_GROUP_NAME}.{ADAFRUIT_IO_HUMIDITY_FEED}", humidity_1)

    except Exception as e:
        log_error(f"Error reading or logging data: {e}")

    if temp_f_1 > SENSOR_THRESHOLD_TEMP:
        SENSOR_ABOVE_THRESHOLD_COUNT += 1
        if SENSOR_ABOVE_THRESHOLD_COUNT >= THRESHOLD_COUNT and not SENSOR_ALERT_SENT:
            sensor_alert_message = (
                f"ALERT: {SENSOR_LOCATION_NAME} Temperature above {SENSOR_THRESHOLD_TEMP}°F\n"
                f"{SENSOR_LOCATION_NAME} Temperature: {temp_f_1:.1f}°F\n"
                f"{SENSOR_LOCATION_NAME} Humidity: {humidity_1}%\n"
            )
            SENSOR_ALERT_SENT = True
    elif temp_f_1 <= SENSOR_THRESHOLD_TEMP and SENSOR_ALERT_SENT:
        sensor_alert_message = (
            f"NOTICE: {SENSOR_LOCATION_NAME} Temperature is now back within range at {temp_f_1:.1f}°F\n"
        )
        SENSOR_ALERT_SENT = False
        SENSOR_ABOVE_THRESHOLD_COUNT = 0

    if sensor_alert_message:
        try:
            tagged_users = " ".join(SLACK_USERS_TO_TAG)
            combined_message_with_tags = f"{tagged_users} {sensor_alert_message}"
            slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=combined_message_with_tags)
        except SlackApiError as e:
            log_error(f"Error posting message to Slack: {e}")
        sensor_alert_message = ""

    time.sleep(60 * MINUTES_BETWEEN_READS)
