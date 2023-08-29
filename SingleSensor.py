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
    config.read(conf_file)  # Read the configuration file
    settings = {}  # Dictionary to store settings
    # List of keys to read from the configuration file
    keys = ['SENSOR_LOCATION_NAME', 'MINUTES_BETWEEN_READS', 'SLACK_API_TOKEN',
            'SLACK_CHANNEL', 'SLACK_USERS_TO_TAG', 'SENSOR_THRESHOLD_TEMP',
            'THRESHOLD_COUNT', 'ADAFRUIT_IO_USERNAME', 'ADAFRUIT_IO_KEY',
            'ADAFRUIT_IO_GROUP_NAME', 'ADAFRUIT_IO_TEMP_FEED', 'ADAFRUIT_IO_HUMIDITY_FEED']
    for key in keys:
        try:
            # Retrieve and type-cast settings based on their expected data type
            if key in ['SENSOR_THRESHOLD_TEMP']:
                settings[key] = config.getfloat('General', key)
            elif key in ['MINUTES_BETWEEN_READS', 'THRESHOLD_COUNT']:
                settings[key] = config.getint('General', key)
            elif key == 'SLACK_USERS_TO_TAG':
                settings[key] = config.get('General', key).split()
            else:
                settings[key] = config.get('General', key)
        except configparser.NoOptionError:
            log_error(f"Missing {key} in configuration file.")  # Log error if any key is missing
            raise
    return settings  # Return the settings dictionary

# Function to log errors into a specified error log file
def log_error(message):
    with open(ERROR_LOG_FILE, 'a') as file:  # Open error log file in append mode
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Get current time
        file.write(f"{timestamp} - ERROR: {message}\n")  # Write the error message with timestamp

# Function to log sensor readings into a specified log file
def log_to_file(sensor_name, temperature, humidity):
    with open(LOG_FILE, 'a') as file:  # Open sensor readings log file in append mode
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Get current time
        file.write(f"{timestamp} - {sensor_name} - Temperature: {temperature}°F, Humidity: {humidity}%\n")  # Log sensor data

# Read settings from the configuration file
settings = read_settings_from_conf('SingleSensorSettings.conf')

# Extract settings into global variables for easier access
for key, value in settings.items():
    globals()[key] = value

# Initialize threshold counter and alert flag for the sensor
SENSOR_ABOVE_THRESHOLD_COUNT = 0
SENSOR_ALERT_SENT = False

# Initialize BME280 sensor
port = 1  # I2C port
address_1 = 0x77  # I2C address for the sensor
bus_1 = smbus2.SMBus(port)  # Initialize the I2C bus
calibration_params_1 = bme280.load_calibration_params(bus_1, address_1)  # Calibration for the sensor

# Initialize Slack client with API token
slack_client = WebClient(token=SLACK_API_TOKEN)

# Initialize Adafruit IO client with username and key
adafruit_io_client = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Initialize empty alert message
sensor_alert_message = ""

# Main loop for reading data, logging, and sending alerts
while True:
    try:
        # Read data from the BME280 sensor
        bme280data_1 = bme280.sample(bus_1, address_1, calibration_params_1)
        humidity_1 = format(bme280data_1.humidity, ".1f")  # Format humidity
        temp_c_1 = bme280data_1.temperature  # Temperature in Celsius
        temp_f_1 = (temp_c_1 * 9 / 5) + 32  # Convert to Fahrenheit
        log_to_file(SENSOR_LOCATION_NAME, temp_f_1, humidity_1)  # Log data

        # Send temperature and humidity to Adafruit IO
        adafruit_io_client.send(f"{ADAFRUIT_IO_GROUP_NAME}.{ADAFRUIT_IO_TEMP_FEED}", temp_f_1)
        adafruit_io_client.send(f"{ADAFRUIT_IO_GROUP_NAME}.{ADAFRUIT_IO_HUMIDITY_FEED}", humidity_1)

    except Exception as e:
        log_error(f"Error reading or logging data: {e}")  # Log errors if any

    # Check if temperature exceeds threshold
    if temp_f_1 > SENSOR_THRESHOLD_TEMP:
        SENSOR_ABOVE_THRESHOLD_COUNT += 1  # Increment the threshold counter
        # Send alert if temperature is above threshold for THRESHOLD_COUNT times
        if SENSOR_ABOVE_THRESHOLD_COUNT >= THRESHOLD_COUNT and not SENSOR_ALERT_SENT:
            sensor_alert_message = (
                f"ALERT: {SENSOR_LOCATION_NAME} Temperature above {SENSOR_THRESHOLD_TEMP}°F\n"
                f"{SENSOR_LOCATION_NAME} Temperature: {temp_f_1:.1f}°F\n"
                f"{SENSOR_LOCATION_NAME} Humidity: {humidity_1}%\n"
            )
            SENSOR_ALERT_SENT = True  # Set the alert sent flag to True

    # Reset alert and counter if temperature is back to normal
    elif temp_f_1 <= SENSOR_THRESHOLD_TEMP and SENSOR_ALERT_SENT:
        sensor_alert_message = (
            f"NOTICE: {SENSOR_LOCATION_NAME} Temperature is now back within range at {temp_f_1:.1f}°F\n"
        )
        SENSOR_ALERT_SENT = False  # Reset the alert sent flag
        SENSOR_ABOVE_THRESHOLD_COUNT = 0  # Reset the threshold counter

    # Send the alert message to Slack if there is any
    if sensor_alert_message:
        try:
            tagged_users = " ".join(SLACK_USERS_TO_TAG)  # Tag specified Slack users
            combined_message_with_tags = f"{tagged_users} {sensor_alert_message}"  # Combine message with tags
            slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=combined_message_with_tags)  # Send Slack message
        except SlackApiError as e:
            log_error(f"Error posting message to Slack: {e}")  # Log errors if any
        sensor_alert_message = ""  # Clear the alert message

    # Sleep for the time specified in the configuration file
    time.sleep(60 * MINUTES_BETWEEN_READS)  # Sleep for the configured number of minutes
