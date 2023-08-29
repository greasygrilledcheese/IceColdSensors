# Troubleshooting Guide for Raspberry Pi Temperature and Humidity Monitoring

This guide aims to assist in resolving common issues related to the Raspberry Pi temperature and humidity monitoring scripts (`dual_sensor_script.py` and `single_sensor_script.py`).

## Table of Contents

- [Sensor Not Responding](#sensor-not-responding)
- [Slack Alerts Not Working](#slack-alerts-not-working)
- [Data Not Logging to Adafruit IO](#data-not-logging-to-adafruit-io)
- [Configuration Errors](#configuration-errors)
- [Unexpected Script Termination](#unexpected-script-termination)

---

## Sensor Not Responding

### Issue

The BME280 sensor does not respond, and no data is being recorded.

### Troubleshooting Steps

1. **Check the Connections**: Ensure all the pins are properly connected.
2. **Check I2C Interface**: Make sure the I2C interface is enabled on your Raspberry Pi.
3. **Test I2C Devices**: Run `i2cdetect -y 1` to see if your Raspberry Pi detects the sensor.
4. **Check Power**: Ensure that the sensor is powered.

---

## Slack Alerts Not Working

### Issue

No alerts are being sent to the Slack channel.

### Troubleshooting Steps

1. **API Token**: Make sure you have provided the correct Slack API token in the configuration file.
2. **Channel Name**: Verify that the Slack channel name in the configuration file exists and is spelled correctly.
3. **Check Permissions**: Make sure the Slack App with the API token has permission to post messages.

---

## Data Not Logging to Adafruit IO

### Issue

Data is not being sent to Adafruit IO feeds.

### Troubleshooting Steps

1. **Check API Key**: Make sure your Adafruit IO API key is correct.
2. **Check Feed Names**: Verify that the feed names in the configuration file match exactly with those on Adafruit IO.
3. **Check Quota**: Make sure you haven't exceeded the data sending limits of your Adafruit IO account.

---

## Configuration Errors

### Issue

The script exits, stating that there are issues with the configuration file.

### Troubleshooting Steps

1. **Check Existence**: Ensure that the configuration file (`DualSensorSettings.conf` or `SingleSensorSettings.conf`) exists in the same directory as the script.
2. **Check Syntax**: Make sure the configuration file is correctly formatted.
3. **Check Values**: Verify that all required keys are present and have values.

---

## Unexpected Script Termination

### Issue

The script terminates unexpectedly during operation.

### Troubleshooting Steps

1. **Check Error Log**: Open `error_log.log` to identify any specific errors that occurred.
2. **Check Resources**: Ensure that the Raspberry Pi has sufficient memory and CPU power to run the script.
3. **Update Packages**: Make sure all Python packages are up to date.

---

For more help, please open an issue in this GitHub repository or consult the `README.md`.
