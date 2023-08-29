# Import necessary libraries
import time  # For time-related functionalities
import smbus2  # For communicating with I2C devices
import bme280  # For BME280 sensor operations
from slack_sdk import WebClient  # For Slack integration
from slack_sdk.errors import SlackApiError  # For Slack error handling
import configparser  # For reading .conf files
from Adafruit_IO import Client  # For Adafruit IO integration

# Define log file locations for storing sensor readings and errors
LOG_FILE = "sensor_readings.log"
ERROR_LOG_FILE = "error_log.log"

# Function to read settings from the configuration file
def read_settings_from_conf(conf_file):
    config = configparser.ConfigParser()  # Initialize configparser
    config.read(conf_file)  # Read the conf file
    settings = {}  # Dictionary to store settings
    # List of keys to read from the conf file
    keys = ['SENSOR_LOCATION_NAME_1', 'SENSOR_LOCATION_NAME_2', 'MINUTES_BETWEEN_READS',
            'SLACK_API_TOKEN', 'SLACK_CHANNEL', 'SLACK_USERS_TO_TAG', 'SENSOR_THRESHOLD_TEMP_1',
            'SENSOR_THRESHOLD_TEMP_2', 'THRESHOLD_COUNT', 'ADAFRUIT_IO_USERNAME', 'ADAFRUIT_IO_KEY',
            'ADAFRUIT_IO_GROUP_NAME']
    for key in keys:
        try:
            # Retrieve and type-cast settings based on their expected data type
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
    return settings  # Return the settings dictionary

# Function to log errors into a specified error log file
def log_error(message):
    with open(ERROR_LOG_FILE, 'a') as file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - ERROR: {message}\n")

# Function to log sensor readings into a specified log file
def log_to_file(sensor_name, temperature, humidity):
    with open(LOG_FILE, 'a') as file:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{timestamp} - {sensor_name} - Temperature: {temperature}°F, Humidity: {humidity}%\n")

# Read settings from the configuration file
settings = read_settings_from_conf('DualSensorSettings.conf')

# Extract settings into global variables for easier access
for key, value in settings.items():
    globals()[key] = value

# Initialize threshold counters and alert flags for sensors
SENSOR_ABOVE_THRESHOLD_COUNT = [0, 0]
SENSOR_ALERT_SENT = [False, False]

# Initialize BME280 sensors
port = 1  # I2C port
address_1 = 0x77  # I2C address for first sensor
address_2 = 0x76  # I2C address for second sensor
bus_1 = smbus2.SMBus(port)  # Initialize the I2C bus
calibration_params_1 = bme280.load_calibration_params(bus_1, address_1)  # Calibration for first sensor
calibration_params_2 = bme280.load_calibration_params(bus_1, address_2)  # Calibration for second sensor

# Initialize Slack client with API token
slack_client = WebClient(token=SLACK_API_TOKEN)

# Initialize Adafruit IO client with username and key
adafruit_io_client = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Main loop for reading data, logging, and sending alerts
while True:
    sensor_alert_messages = ["", ""]  # Initialize empty alert messages
    # Iterate through sensors to read data and check conditions
    for sensor_index, (address, calibration_params, sensor_location_name, threshold_temp) in enumerate([
        (address_1, calibration_params_1, SENSOR_LOCATION_NAME_1, SENSOR_THRESHOLD_TEMP_1),
        (address_2, calibration_params_2, SENSOR_LOCATION_NAME_2, SENSOR_THRESHOLD_TEMP_2)
    ]):
        try:
            # Read data from the BME280 sensors
            bme280data = bme280.sample(bus_1, address, calibration_params)
            humidity = format(bme280data.humidity, ".1f")  # Format humidity
            temp_c = bme280data.temperature  # Temperature in Celsius
            temp_f = (temp_c * 9 / 5) + 32  # Convert to Fahrenheit
            log_to_file(sensor_location_name, temp_f, humidity)  # Log data
            
            # Send temperature and humidity to Adafruit IO
            adafruit_io_client.send(f'{ADAFRUIT_IO_GROUP_NAME}.{sensor_location_name}_temperature', temp_f)
            adafruit_io_client.send(f'{ADAFRUIT_IO_GROUP_NAME}.{sensor_location_name}_humidity', humidity)
            
            # Check if temperature exceeds threshold
            if temp_f > threshold_temp:
                SENSOR_ABOVE_THRESHOLD_COUNT[sensor_index] += 1
                # Send alert if above threshold for THRESHOLD_COUNT times
                if SENSOR_ABOVE_THRESHOLD_COUNT[sensor_index] >= THRESHOLD_COUNT and not SENSOR_ALERT_SENT[sensor_index]:
                    sensor_alert_messages[sensor_index] = (
                        f"ALERT: {sensor_location_name} Temperature above {threshold_temp}°F\n"
                        f"{sensor_location_name} Temperature: {temp_f:.1f}°F\n"
                        f"{sensor_location_name} Humidity: {humidity}%\n"
                    )
                    SENSOR_ALERT_SENT[sensor_index] = True
            # Reset alert and counter if temperature is back to normal
            elif temp_f <= threshold_temp and SENSOR_ALERT_SENT[sensor_index]:
                sensor_alert_messages[sensor_index] = (
                    f"NOTICE: {sensor_location_name} Temperature is now back within range at {temp_f:.1f}°F\n"
                )
                SENSOR_ALERT_SENT[sensor_index] = False
                SENSOR_ABOVE_THRESHOLD_COUNT[sensor_index] = 0

        except Exception as e:
            log_error(f"Error reading or logging data for sensor {sensor_location_name}: {e}")

    # Send alert messages to Slack channel
    for sensor_alert_message in sensor_alert_messages:
        if sensor_alert_message:  # Only send if there is an alert
            try:
                tagged_users = " ".join(SLACK_USERS_TO_TAG)  # Tag specified Slack users
                combined_message_with_tags = f"{tagged_users} {sensor_alert_message}"
                slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=combined_message_with_tags)  # Send message
            except SlackApiError as e:
                log_error(f"Error posting message to Slack: {e}")

    # Sleep for the time specified in the configuration file
    time.sleep(60 * MINUTES_BETWEEN_READS)

