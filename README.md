ICECOLDSENSORS
--------------------------------------

Requirements
------------
- Python 3.x
- Required Python libraries:
  - time
  - smbus2
  - bme280
  - ISStreamer
  - slack_sdk
  - configparser

Installation
------------
1. Clone the repository or download the script `sensor_data_logger.py` to your local machine.

2. Install the required Python libraries using pip:

   `pip install smbus2 bme280-pi slack_sdk configparser`

Configuration
-------------
Before running the script, you need to configure the `settings.conf` file. The `settings.conf` file contains various settings required for the script to function correctly. Make sure to fill in the appropriate values for each setting.

Here's how to configure the `settings.conf` file:
<code>
[General]
SENSOR_LOCATION_NAME_1 = Freezer
SENSOR_LOCATION_NAME_2 = Fridge
BUCKET_NAME = your_initial_state_bucket_name
BUCKET_KEY = your_initial_state_bucket_key
ACCESS_KEY = your_initial_state_access_key
MINUTES_BETWEEN_READS = 5
SLACK_API_TOKEN = your_slack_api_token
SLACK_CHANNEL = your_slack_channel_name
SLACK_USERS_TO_TAG = slack_user_id1 slack_user_id2
FREEZER_THRESHOLD_TEMP = 17
FRIDGE_THRESHOLD_TEMP = 40
THRESHOLD_COUNT = 3
</code>
- Replace your_initial_state_bucket_name, your_initial_state_bucket_key, and your_initial_state_access_key with your Initial State credentials.
- Replace your_slack_api_token with your Slack API token and your_slack_channel_name with the desired Slack channel to post alerts.
- Add the Slack user IDs (space-separated) of users you want to tag when an alert is triggered.

Usage
-----
1. Make sure the settings.conf file is properly filled out with your configurations.

2. Run the script using Python:

   python sensor_data_logger.py

3. The script will continuously read data from the Freezer and Fridge BME280 sensors at the specified interval (MINUTES_BETWEEN_READS). The data will be logged to the Initial State platform.

4. If the temperature in the Freezer or Fridge exceeds the predefined thresholds (FREEZER_THRESHOLD_TEMP and FRIDGE_THRESHOLD_TEMP) for a specified number of consecutive readings (THRESHOLD_COUNT), a Slack alert will be triggered, and the specified users will be tagged.

5. The script will keep running until manually stopped (e.g., using Ctrl+C).

----
Note
----
Ensure that the I2C addresses of the BME280 sensors (0x77 for Freezer and 0x76 for Fridge) are correctly configured in the script and match the actual sensor addresses.
