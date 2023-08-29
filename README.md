# Raspberry Pi Temperature and Humidity Monitoring

This repository contains two Python scripts to monitor temperature and humidity using BME280 sensors on a Raspberry Pi. The scripts send alerts via Slack and log data to Adafruit IO.

- `dual_sensor_script.py`: For monitoring two BME280 sensors.
- `single_sensor_script.py`: For monitoring a single BME280 sensor.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Hardware Setup](#hardware-setup)
- [Software Setup](#software-setup)
- [Configuration Files](#configuration-files)
- [Adafruit IO Setup](#adafruit-io-setup)
- [Running the Scripts](#running-the-scripts)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Raspberry Pi (Any model with GPIO pins will work)
- BME280 sensor(s)
- Jumper wires
- Breadboard (optional)
- Internet connection
- Slack Workspace
- Adafruit IO account

## Hardware Setup

### Enabling I2C on Raspberry Pi

1. Open the Raspberry Pi configuration menu: `sudo raspi-config`
2. Navigate to `Interface Options > I2C` and enable it.
3. Reboot your Raspberry Pi.

### Connecting BME280 Sensor(s)

- Connect the `VCC` pin of the BME280 to `3.3V` on the Raspberry Pi.
- Connect the `GND` pin to `Ground`.
- Connect the `SDA` pin to `SDA` (GPIO 2).
- Connect the `SCL` pin to `SCL` (GPIO 3).

If you are using two BME280 sensors, you can connect them in parallel to the same SDA and SCL lines. Be sure to ground one of the sensors' `SDO` pins; this sensor will be addressed at `0x76`.

## Software Setup

1. Update your Raspberry Pi: `sudo apt update && sudo apt upgrade`
2. Install the required Python packages:

    ```bash
    pip install smbus2 bme280 slack_sdk Adafruit_IO
    ```

## Configuration Files

Create configuration files named `DualSensorSettings.conf` and `SingleSensorSettings.conf` with appropriate settings. Samples are provided in the repository.

## Adafruit IO Setup

1. Log in to your Adafruit IO account or create one if you don't have it.
2. Navigate to `Dashboards` and create a new dashboard for your sensors.
3. Add blocks (e.g., gauge, chart) to your dashboard.
4. Go to `Feeds` and create new feeds for temperature and humidity.
5. Make sure to update the `ADAFRUIT_IO_USERNAME`, `ADAFRUIT_IO_KEY`, `ADAFRUIT_IO_GROUP_NAME`, `ADAFRUIT_IO_TEMP_FEED`, and `ADAFRUIT_IO_HUMIDITY_FEED` in your configuration files to match your Adafruit IO setup.

## Running the Scripts

1. Clone this repository:

    ```bash
    git clone <repository_url>
    ```

2. Navigate into the directory:

    ```bash
    cd <repository_directory>
    ```

3. Run the script:

    - For dual sensors:
    
        ```bash
        python dual_sensor_script.py
        ```
    
    - For a single sensor:
    
        ```bash
        python single_sensor_script.py
        ```

## Troubleshooting

- Make sure I2C is enabled and that the sensor is correctly connected.
- Check the log files `sensor_readings.log` and `error_log.log` for debugging information.

---

For more help, please open an issue in this GitHub repository.
