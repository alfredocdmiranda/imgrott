# ImGrott
![](docs/images/imgrott.jpg)
> **NOTE**:
> This project is forked from the amazing project [Grott](https://github.com/johanmeijer/grott), 
> based on the stable version **2.7.8**.
> 
> This fork was created aiming to improve its maintainability, readability and allow to community easily contribute with 
> fixes and new features.

Growatt inverters can send performance and status metrics (log data) to the Growatt company servers. 
The inverters rely on either a ShineWIFI module or a ShineLAN box to relay the data to Growatt. 
The metrics stored on the Growatt servers then can be viewed on the Growatt website or using the ShinePhone mobile app.

The purpose of ImGrott is to read, parse, forward the *raw metrics as they are sent* to Growatt servers and be able to 
send these data to other applications(e.g.: MQTT, InfluxDB). This means other applications can consume the raw Growatt 
metrics without relying on the Growatt API and servers and without delay.

## Requirements

- Python 3.7+
- influxdb
- influxdb-client
- paho-mqtt
- requests

You can either install these packages manually or run the following command:
```
$ pip install -r requirements.txt
```

## Installation

In order to run the server, you can just run `grott.py`. You are going to need to create a `grott.ini` file (you can 
find an example file in `examples` directories).

```
$python -u grott.py -v
```

## Setting up

There is two modes to run, `proxy` and `sniff` mode.
- [Sniff Mode](docs/setup/sniff_mode.md) (deprecated)
- [Proxy Mode](docs/setup/proxy_mode.md)

Please, check if your device is supported.

## Features

- Forward data to Growatt servers
- Accept commands from Growatt server
- Send data to a [MQTT](https://mqtt.org/) server
- Send to [InfluxDB](https://www.influxdata.com/)
- Send data to [PVOutput](https://pvoutput.org/)
- Send data to custom extension

### Supported Inverters

| Inverter      | Datalogger  | Status    |
|---------------|-------------|-----------|
| 1500-S        | ShineWiFi   | Supported |
| 1500TL-X      | ShineWiFi-X | Supported |
| 2500-MTL-S    | ShineWiFi   | Supported |
| 3000-S        | ShineLan    | Supported |
| 3600TL-XE     | ShineLan    | Supported |
| 3600TL-XE     | ShineLink-X | Supported |
| 4200-MTL-S    | ShineWiFi-X | Supported |
| 5000TL-X      | ShineWiFi-X | Supported |
| MOD 5000TL3-X | ShineLan    | Supported |
| MOD 9000TL3-X | ShineLan    | Supported |

If you have tested in a different inverter or datalogger, and it is working fine, please create a PR.

### Supported Systems
- Linux
- Windows
