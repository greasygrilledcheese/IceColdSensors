ICECOLDSENSORS - IoT Temperature Monitoring and Alert System with Raspberry Pi, BME280 Sensors, Initial State, and Slack Integration
--------------------------------------
Detailed instructions [HERE](https://sethmorrow.com/sensors/)

⚠️ Notice: The Slack tagged users functionality is currently experiencing issues and is not functioning as expected. For the time being, please leave the line related to tagged users in the config file blank until the problem is resolved. We are actively investigating and will update as soon as it's fixed. Thank you for your patience!

# Python Script for Monitoring Fridge and Freezer Temperatures

This script reads temperature and humidity data from BME280 sensors connected to a Raspberry Pi. The data is then logged to Initial State and checked against predefined thresholds. If the temperature of either the fridge or freezer exceeds its threshold for a certain number of consecutive readings, an alert message is sent to a specified Slack channel.

## Requirements

1. **Hardware:** The BME280 sensors must be properly connected to the Raspberry Pi's I2C port and should be reachable at the I2C addresses `0x77` and `0x76`.
2. **Python Libraries:** The following Python libraries must be installed:
   - `smbus2`
   - `bme280`
   - `ISStreamer.Streamer`
   - `slack_sdk`
   - `configparser`
   - `time` (standard library)
3. **Initial State Service:** You must have access to the Initial State service for data logging, and a valid bucket to log data to.
4. **API Tokens & Channel Names:** The API tokens and channel names for Initial State and Slack must be correctly configured in the `.conf` file.
5. **Script Permissions:** The script must have the necessary permissions to access these services.

## Configuration

The script reads settings from a `.conf` file named `IceColdSettings.conf`. This file should include the following keys under a `[General]` section:

- `SENSOR_LOCATION_NAME_1`: The name of the location of the first sensor.
- `SENSOR_LOCATION_NAME_2`: The name of the location of the second sensor.
- `BUCKET_NAME`: The name of the Initial State bucket where the data is logged.
- `BUCKET_KEY`: The key of the Initial State bucket.
- `ACCESS_KEY`: The access key for Initial State.
- `MINUTES_BETWEEN_READS`: The number of minutes to wait between sensor readings.
- `SLACK_API_TOKEN`: The API token for Slack.
- `SLACK_CHANNEL`: The Slack channel where alert messages are sent.
- `SLACK_USERS_TO_TAG`: A space-separated list of Slack user IDs to tag in alert messages.
- `FREEZER_THRESHOLD_TEMP`: The temperature threshold for the freezer.
- `FRIDGE_THRESHOLD_TEMP`: The temperature threshold for the fridge.
- `THRESHOLD_COUNT`: The number of consecutive readings above the threshold that triggers an alert.

## Execution

Run the script using a Python 3 interpreter. The script will read data from the sensors, log the data to Initial State, and check if the temperature is above the threshold. If the temperature is above the threshold for a specified number of consecutive readings, an alert message will be sent to Slack.


----
Note
----
Ensure that the I2C addresses of the BME280 sensors (0x77 for Freezer and 0x76 for Fridge) are correctly configured in the script and match the actual sensor addresses.
