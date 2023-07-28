# IceColdSensors

#NOTE: This is highly modified version of the script available in this tutorial:
#https://medium.com/initial-state/how-to-build-a-raspberry-pi-refrigerator-freezer-monitor-f7a91075c2fd

This code is a Python script designed to monitor the temperature and humidity of a freezer and a fridge using two BME280 sensors connected to a Raspberry Pi. It also sends alerts to a Slack channel if the temperature in either the freezer or fridge exceeds certain thresholds for a specified number of consecutive readings.

Here's an overview of how the code works:

Import necessary libraries:

time: Used for adding delays between sensor readings.
smbus2: A Python library for I2C communication on Raspberry Pi.
bme280: A library for interacting with the BME280 sensor to read temperature and humidity data.
ISStreamer.Streamer: A library for logging data to Initial State, a data visualization platform.
slack_sdk: A library for interacting with the Slack API to send messages.
User Settings: This section contains various customizable settings that the user can modify according to their needs. They include names for the freezer and fridge, Initial State bucket name and key, access key for Initial State, time interval between sensor readings (MINUTES_BETWEEN_READS), and the Slack API token.

Initializing variables and objects: This section sets up the necessary variables and objects for the BME280 sensors, the Initial State streamers, and the Slack client.

Main Loop: The main loop runs indefinitely, continuously reading data from both the freezer and fridge sensors and performing actions based on the readings.

For the Freezer (Sensor 1):

It reads temperature and humidity data from the BME280 sensor.
Logs the data to the Initial State streamer object for the freezer.
Checks if the freezer temperature is above 17°F for four consecutive readings (THRESHOLD_COUNT).
If the condition is met, it sends an alert to the Slack channel, indicating the consecutive intervals where the temperature was above 17°F.
For the Fridge (Sensor 2):

It reads temperature and humidity data from the BME280 sensor.
Logs the data to the Initial State streamer object for the fridge.
Checks if the fridge temperature is above 40°F for four consecutive readings (THRESHOLD_COUNT).
If the condition is met, it sends an alert to the Slack channel, indicating the consecutive intervals where the temperature was above 40°F.
After processing the data for both the freezer and fridge, the script sleeps for the specified interval (MINUTES_BETWEEN_READS) before the next iteration.

It's important to note that the code requires proper hardware setup, including connecting the BME280 sensors to the Raspberry Pi's I2C bus and obtaining the correct I2C addresses for the sensors. Additionally, the user needs to provide their own values for the Initial State bucket and access key, as well as the Slack API token and Slack channel where the alerts will be posted.

As this code was based on a modified version of a script from Medium, it's always a good 
