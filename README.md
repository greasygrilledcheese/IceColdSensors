# IceColdSensors

NOTE: This is highly modified version of the script available in this tutorial:
https://medium.com/initial-state/how-to-build-a-raspberry-pi-refrigerator-freezer-monitor-f7a91075c2fd

# Temperature and Humidity Monitoring System with InitialState and Slack Integration

## Overview
This Python script is designed to monitor temperature and humidity in two distinct locations, namely a Freezer and a Fridge, using two separate BME280 sensors. These sensors are connected to a single Raspberry Pi using the I2C (Inter-Integrated Circuit) communication protocol. The script collects data from the sensors, logs it to the Initial State cloud service, and sends alerts to a designated Slack channel if certain temperature thresholds are exceeded.

## Requirements
To run this script, you need the following:
- Python with necessary libraries: `time`, `smbus2`, `bme280`, `ISStreamer`, `slack_sdk`
- Access to the Initial State cloud service
- A Slack API token for posting messages to a Slack channel

## Setup
1. Import the necessary libraries required for the script to function.
2. Define user settings that will be used in the script, such as sensor names, Initial State bucket details, access key, and time interval between sensor readings.
3. Initialize Slack API settings by providing your Slack API token.

## I2C and BME280 Setup
Two BME280 sensors are connected to the Raspberry Pi using the I2C communication protocol. I2C is a widely used serial communication protocol that allows multiple devices to communicate with each other over a shared bus. The Raspberry Pi acts as the master on the I2C bus, while the BME280 sensors act as slaves. Each sensor is configured with a unique I2C address.

- The first BME280 sensor, associated with the Freezer, is configured with the I2C address 0x77.
- The second BME280 sensor, corresponding to the Fridge, is configured with the I2C address 0x76.

## Main Loop
The main loop continuously reads data from the two BME280 sensors. It performs the following steps for each sensor:

### For Freezer (Sensor 1):
1. Read temperature and humidity data from the BME280 sensor associated with the Freezer.
2. Log the collected data to the Initial State bucket associated with the Freezer.
3. Check if the Freezer temperature is above 17°F for 3 consecutive MINUTES_BETWEEN_READS intervals.
4. If the threshold is met, send an alert message to a specified Slack channel.
5. Sleep for the specified interval before proceeding to the next iteration.

### For Fridge (Sensor 2):
1. Read temperature and humidity data from the BME280 sensor associated with the Fridge.
2. Log the collected data to the Initial State bucket associated with the Fridge.
3. Check if the Fridge temperature is above 40°F for 3 consecutive MINUTES_BETWEEN_READS intervals.
4. If the threshold is met, send an alert message to a specified Slack channel.
5. Sleep for the specified interval before proceeding to the next iteration.

## Functionality Breakdown

1. Import necessary libraries and modules.
2. User Settings - Customize these variables according to your needs.
3. Initialize Slack API settings.
4. Counter variables for temperature MINUTES_BETWEEN_READS intervals and the threshold count.
5. BME280 sensor settings for Freezer and Fridge.
6. Initialize the Initial State streamer objects for each sensor.
7. Main loop for continuous monitoring and data logging.

## Running the Script
Before running the script, ensure you have replaced the placeholder values such as `"Your-Key-Here"` and `"your-slack-api-token"` with appropriate access keys and tokens. This script can be executed on a Raspberry Pi or any other suitable platform with I2C support to monitor the temperature and humidity of the Freezer and Fridge locations. The data is then logged to Initial State, and alerts are sent to the designated Slack channel if certain temperature thresholds are exceeded for a defined number of consecutive readings.
