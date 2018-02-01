# th-mon
Temperature and humidity server room monitor using DHT22's and Raspberry Pis

This project was created so that I could monitor server rooms that I have equipment in to make sure the environment is not in danger due to A/C failures. It was also useful to see how ramping up a cluster of HPC machines would affect server room temperatures.

To use this project, you will need:
  - A Raspberry Pi
  - A DHT22 sensor
  - A 4.7K pull-up resistor between the DHT22 pin 1 and 2 (if not already included)

The [bin/sensor.py](bin/sensor.py) script can be run from a cron job or as a systemd service. Every 5 minutes will work well.

After cloning the repo, you will need to pull in Adafruit Python library for working with the DHT sensors.

```git submodule init```

```git submodule update```

