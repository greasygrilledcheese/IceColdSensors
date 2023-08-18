# Import necessary libraries

# Streamer is for logging data to Initial State platform
from ISStreamer.Streamer import Streamer

# smbus2 and bme280 libraries facilitate communication with the BME280 sensor over I2C.
import smbus2
import bme280

# slack_sdk is used for sending messages to Slack.
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# configparser helps in parsing the configuration file that holds various settings.
import configparser

# logging library provides a way to log messages (like errors or information). 
# time library helps in introducing pauses in the program.
import logging
import time

# Define the path of the configuration file.
CONFIG_FILE = 'IceColdSettings.conf'

def read_settings_from_conf(conf_file):
    """Reads configuration settings from the provided file and returns them as a dictionary."""
    # Instantiate a ConfigParser object
    config = configparser.ConfigParser()
    # Read the configuration from the given file
    config.read(conf_file)

    # List of keys that are expected to be present in the configuration file
    required_keys = [
        'SENSOR_LOCATION_NAME_1', 'SENSOR_LOCATION_NAME_2', 'BUCKET_NAME',
        'BUCKET_KEY', 'ACCESS_KEY', 'MINUTES_BETWEEN_READS', 'SLACK_API_TOKEN',
        'SLACK_CHANNEL', 'SLACK_USERS_TO_TAG', 'FREEZER_THRESHOLD_TEMP',
        'FRIDGE_THRESHOLD_TEMP', 'THRESHOLD_COUNT', 'BUS_1', 'BUS_1_ADDRESS', 'BUS_2', 'BUS_2_ADDRESS'
    ]

    # Check if each required key is present in the configuration
    for key in required_keys:
        if key not in config['General']:
            # Log the error and raise an exception if a key is missing
            logging.error(f"Key {key} missing in the configuration file.")
            raise KeyError(f"Key {key} missing in the configuration file.")
    
    # Convert comma-separated string of slack users into a list
    config['General']['SLACK_USERS_TO_TAG'] = config.get('General', 'SLACK_USERS_TO_TAG').split(',')

    # Return the parsed settings as a dictionary
    return {key: config.get('General', key) for key in required_keys}

def read_and_log_sensor(bus_num, address, calibration_params, sensor_name, streamer):
    """Reads data from the BME280 sensor and logs it."""
    # Initialize the I2C bus using the specified bus number
    bus = smbus2.SMBus(int(bus_num))
    try:
        # Sample data from the BME280 sensor using the given calibration parameters
        bme280data = bme280.sample(bus, address, calibration_params)
        # Format humidity to one decimal place
        humidity = format(bme280data.humidity, ".1f")
        # Convert Celsius temperature reading to Fahrenheit
        temp_c = bme280data.temperature
        temp_f = (temp_c * 9 / 5) + 32
        # Log the readings to Initial State
        streamer.log(f"{sensor_name} Temperature(F)", temp_f)
        streamer.log(f"{sensor_name} Humidity(%)", humidity)
        streamer.flush()  # Ensure data is sent to Initial State immediately
        # Log the sensor readings to the console or log file
        logging.info(f"{sensor_name} - Temperature: {temp_f}°F, Humidity: {humidity}%")
        return temp_f, humidity
    except Exception as e:
        # If there's any error during reading or logging, log the error and return None values
        logging.error(f"Error reading or logging data: {e}")
        return None, None
    finally:
        # Close the I2C bus connection
        bus.close()

def check_threshold(temp, threshold_temp, sensor_name, alert_sent, above_threshold_count, settings):
    """Checks if the temperature exceeds the threshold and returns updated alert and count states."""
    # If there's no temperature reading, return current states
    if temp is None:
        return alert_sent, above_threshold_count, ""

    # Initialize alert_message as an empty string
    alert_message = ""
    # Check if the temperature reading exceeds the threshold
    if temp > threshold_temp:
        above_threshold_count += 1
        # If readings have exceeded threshold for a certain consecutive count and no alert has been sent yet, send an alert
        if above_threshold_count >= int(settings['THRESHOLD_COUNT']) and not alert_sent:
            alert_message = f"ALERT: {sensor_name} Temperature above {threshold_temp}°F\nCurrent Temperature: {temp:.1f}°F\n"
            alert_sent = True
    # If temperature is within range and an alert was previously sent, send a notice
    elif temp <= threshold_temp and alert_sent:
        alert_message = f"NOTICE: {sensor_name} Temperature is now back within range at {temp:.1f}°F\n"
        alert_sent = False
        above_threshold_count = 0

    # Return the updated states and any alert message that needs to be sent
    return alert_sent, above_threshold_count, alert_message

def send_slack_alert(alert_message, settings, slack_client):
    """Sends an alert message to Slack."""
    # Construct a message tagging the specified Slack users
    tagged_users = " ".join(settings['SLACK_USERS_TO_TAG'])
    combined_message_with_tags = f"{tagged_users} {alert_message}"
    
    try:
        # Post the message to the specified Slack channel
        slack_client.chat_postMessage(channel=settings['SLACK_CHANNEL'], text=combined_message_with_tags)
    except SlackApiError as e:
        # Log any errors that occur while posting to Slack
        logging.error(f"Error posting message to Slack: {e}")

def main():
    """Main function to run the script."""
    # Load settings from the configuration file
    settings = read_settings_from_conf(CONFIG_FILE)

    # Initialize states for alerts and counts for freezer and fridge
    FRIDGE_ALERT_SENT = False
    FREEZER_ALERT_SENT = False
    FREEZER_ABOVE_THRESHOLD_COUNT = 0
    FRIDGE_ABOVE_THRESHOLD_COUNT = 0

    # Fetch the I2C addresses for the two sensors from the settings
    address_1 = settings['BUS_1_ADDRESS']
    address_2 = settings['BUS_2_ADDRESS']

    # Load calibration parameters for both sensors
    calibration_params_1 = bme280.load_calibration_params(smbus2.SMBus(int(settings['BUS_1'])), address_1)
    calibration_params_2 = bme280.load_calibration_params(smbus2.SMBus(int(settings['BUS_2'])), address_2)

    # Initialize data streamers for both sensors with the specified bucket information
    streamer_1 = Streamer(bucket_name=settings['BUCKET_NAME'], bucket_key=settings['BUCKET_KEY'], access_key=settings['ACCESS_KEY'])
    streamer_2 = Streamer(bucket_name=settings['BUCKET_NAME'], bucket_key=settings['BUCKET_KEY'], access_key=settings['ACCESS_KEY'])

    # Initialize Slack client with the provided API token
    slack_client = WebClient(token=settings['SLACK_API_TOKEN'])

    while True:  # Infinite loop to continuously check temperatures and alert as necessary
        # Read and log sensor data for both sensors
        temp_1, _ = read_and_log_sensor(settings['BUS_1'], address_1, calibration_params_1, settings['SENSOR_LOCATION_NAME_1'], streamer_1)
        temp_2, _ = read_and_log_sensor(settings['BUS_2'], address_2, calibration_params_2, settings['SENSOR_LOCATION_NAME_2'], streamer_2)

        # Check if temperatures exceed thresholds and get any alert messages to send
        FREEZER_ALERT_SENT, FREEZER_ABOVE_THRESHOLD_COUNT, alert_message_1 = check_threshold(temp_1, float(settings['FREEZER_THRESHOLD_TEMP']), settings['SENSOR_LOCATION_NAME_1'], FREEZER_ALERT_SENT, FREEZER_ABOVE_THRESHOLD_COUNT, settings)
        FRIDGE_ALERT_SENT, FRIDGE_ABOVE_THRESHOLD_COUNT, alert_message_2 = check_threshold(temp_2, float(settings['FRIDGE_THRESHOLD_TEMP']), settings['SENSOR_LOCATION_NAME_2'], FRIDGE_ALERT_SENT, FRIDGE_ABOVE_THRESHOLD_COUNT, settings)

        # If there are any alerts to send, send them to Slack
        if alert_message_1:
            send_slack_alert(alert_message_1, settings, slack_client)
        if alert_message_2:
            send_slack_alert(alert_message_2, settings, slack_client)

        # Wait for the specified duration before the next readings
        time.sleep(int(settings['MINUTES_BETWEEN_READS']) * 60)

if __name__ == "__main__":
    main()  # Run the main function when the script is executed
