# Raspberry Pi Temperature and Humidity Monitoring

This repository contains two Python scripts for monitoring temperature and humidity using BME280 sensors on a Raspberry Pi. The scripts send alerts via Slack and log data to Adafruit IO.

- `dual_sensor_script.py`: For monitoring two BME280 sensors.
- `single_sensor_script.py`: For monitoring a single BME280 sensor.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Hardware Setup](#hardware-setup)
- [Software Setup](#software-setup)
- [Configuration Files](#configuration-files)
- [Adafruit IO Setup](#adafruit-io-setup)
- [Running the Scripts](#running-the-scripts)
- [Start Script on Boot](#start-script-on-boot)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Raspberry Pi (Any model with GPIO pins will work)
- BME280 sensor(s)
- Jumper wires
- Breadboard (optional)
- Internet connection
- Slack Workspace
- Adafruit IO account

## Initial Setup

### Enable SSH and WiFi

1. Place a file named `ssh` (no extension) in the root directory of the boot partition to enable SSH.
2. Create a `wpa_supplicant.conf` file in the same boot partition with the following content:

    ```bash
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=<Your-Country-Code>

    network={
        ssid="<Your-SSID>"
        psk="<Your-Password>"
    }
    ```
Replace `<Your-Country-Code>`, `<Your-SSID>`, and `<Your-Password>` with your country code, WiFi name, and WiFi password, respectively.

3. Insert the SD card back into the Raspberry Pi and boot it up. It should connect to the WiFi network, and SSH should be enabled.

## Hardware Setup

### Enabling I2C on Raspberry Pi

1. Open the Raspberry Pi configuration menu: `sudo raspi-config`
2. Navigate to `Interface Options > I2C` and enable it.
3. Reboot your Raspberry Pi.

### Connecting BME280 Sensor(s)

- Follow the [Prerequisites](#prerequisites) section for hardware details.

## Software Setup

1. Update your Raspberry Pi: `sudo apt update && sudo apt upgrade`
2. Install the required Python packages:

    ```bash
    pip install smbus2 bme280 slack_sdk Adafruit_IO
    ```

## Configuration Files

Create configuration files with appropriate settings. Samples are provided in the repository.

## Adafruit IO Setup

Follow the steps outlined in the [Adafruit IO Setup](#adafruit-io-setup) section.

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

## Start Script on Boot

To make the script run automatically on boot, use `crontab`:

1. Open crontab configuration:

    ```bash
    crontab -e
    ```

2. Choose `nano` as the editor if prompted.

3. Add the following line at the end of the file:

    ```bash
    @reboot python /path/to/your/script.py &
    ```

Replace `/path/to/your/script.py` with the full path to your Python script.

4. Save the file and exit `nano`.

## Troubleshooting

For troubleshooting, please refer to the `Troubleshooting.md` file in this repository.

---

For more help, please open an issue in this GitHub repository.

