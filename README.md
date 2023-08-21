# Raspberry Pi Temperature and Humidity Monitoring

This guide provides detailed instructions on how to set up and utilize these Python scripts to monitor temperature and humidity using BME280 sensors on a Raspberry Pi. These scripts are designed to offer comprehensive monitoring, logging, alerting via Slack, and integration with Adafruit IO for online data visualization.

⚠️ Notice: Slack alerts are working, but the Slack tagged users functionality is currently experiencing issues and is not working properly. For the time being, please leave the line related to tagged users in the config file blank until the problem is resolved.

## Table of Contents

- [Pre-Requisites](#pre-requisites)
- [Instructions](#instructions)
  - [1. Connect BME280 Sensor(s)](#1-connect-bme280-sensors)
  - [2. Create Configuration File](#2-create-configuration-file)
  - [3. Install Required Libraries](#3-install-required-libraries)
  - [4. Prepare Script](#4-prepare-script)
  - [5. Run the Script](#5-run-the-script)
  - [6. Logging and Alerts](#6-logging-and-alerts)
  - [7. Monitor Through Adafruit IO](#7-monitor-through-adafruit-io)
  - [8. Automate Script Startup (Optional)](#8-automate-script-startup-optional)
- [Conclusion](#conclusion)

## Pre-Requisites

- **Hardware Requirements**: Raspberry Pi Zero (with GPIO pins), one or two BME280 sensors, connecting cables.
- **Software Requirements**: Raspberry Pi OS (Raspbian), Python installed, required Python libraries (\`smbus2\`, \`bme280\`, \`slack_sdk\`, \`Adafruit_IO\`).

## Instructions

### 1. Connect BME280 Sensor(s)

- Connect the BME280 sensor(s) to the Raspberry Pi as follows:
  - Connect the VCC pin of the sensor to the 3.3V pin on the Raspberry Pi.
  - Connect the GND pin of the sensor to the ground (GND) pin on the Raspberry Pi.
  - Connect the SDA pin of the sensor to the SDA pin on the Raspberry Pi.
  - Connect the SCL pin of the sensor to the SCL pin on the Raspberry Pi.
  - If you're using two sensors, set one sensor's address to 0x77 and the other's address to 0x76 by adjusting grounding the SDO pin of one of the sensors. This sensor will be addressed at 0x76.

### 2. Create Configuration File

- Create a configuration file named `IceColdSettings.conf` with the following format:
  ```ini
  [General]
  SENSOR_LOCATION_NAME=Location_Name
  MINUTES_BETWEEN_READS=5
  SLACK_API_TOKEN=your_slack_api_token
  SLACK_CHANNEL=channel_name
  SLACK_USERS_TO_TAG=user1 user2
  SENSOR_THRESHOLD_TEMP=70.0
  THRESHOLD_COUNT=3
  ADAFRUIT_IO_USERNAME=your_adafruit_io_username
  ADAFRUIT_IO_KEY=your_adafruit_io_key
  ```
  Adjust the values according to your preferences.

### 3. Install Required Libraries

- Open a terminal on the Raspberry Pi and install the necessary Python libraries:
  ```bash
  pip install smbus2 bme280 slack-sdk Adafruit_IO
  ```

### 4. Prepare Script

- Choose the script that corresponds to the number of BME280 sensors you are using:
  - If you have one sensor, save the script named `SingleSensor.py`.
  - If you have two sensors, save the script named `DualSensors.py`.

### 5. Run the Script

- Open a terminal and navigate to the location where you saved the script:
  ```bash
  python SingleSensor.py   # For one sensor
  python DualSensors.py   # For two sensors
  ```

### 6. Logging and Alerts

- The script logs sensor readings in the `sensor_readings.log` file and records errors in the `error_log.log` file.
- If the temperature crosses the threshold defined in the configuration, an alert will be sent to the specified Slack channel, tagging the mentioned users.

### 7. Monitor Through Adafruit IO

- The script sends temperature and humidity readings to Adafruit IO, allowing you to visualize the data online.

### 8. Automate Script Startup (Optional)

To have the monitoring script start automatically on boot, follow these steps:

- Open a terminal on your Raspberry Pi Zero.
- Open the crontab configuration using the nano text editor (if prompted, choose nano`):
  ```bash
  crontab -e
  ```
- Add the following line to the crontab file to run the script on boot:
  ```bash
  @reboot nohup python3 /path/to/your/script.py
  ```
  Replace `/path/to/your/script.py` with the actual path to your monitoring script.
- Save the file and exit the text editor.
- The script will now run automatically every time your Raspberry Pi Zero boots up.
  
## Conclusion

These scripts offer a comprehensive solution for monitoring temperature and humidity using BME280 sensors and a Raspberry Pi. Ensure correct connections, configure the settings, and run the script to initiate monitoring. 




