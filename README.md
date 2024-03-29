# Networkscan
> Raspberry Pi automatic network device scanner - specific tcp port status and default password checker for various vendors
## Table of Contents
- [Usage](#Usage)
- [How it works](#How-it-works)
- [Requirements](#Requirements)
- [Installation](#Installation)
- [Supported vendors](#Supported-vendors)
- [Author](#Author)
- [License](#License)

## Usage

- **Power on Raspberry Pi using power bank for portability and stealth**
- **Connect Raspberry Pi network interface to target network**
- **Network scanning will begin automatically without user intervention**
- **Scanned results will be automatically sent to your phone for stealthy network inspection**
- **Keep scanning other networks without interruption by plugging network cable in other target network**

## How it works
### Raspberry Pi
![Process flow diagram](process_flow_diagram.png)
### Service behavior - Interface UP
- **Start python networkscan software**
    - Scan network hosts with Nmap
    - Scan defined open ports for found vendor hosts
    - Do http auth request with default manufacturer credentials
- **Write scanned results to /tmp/output.txt**
- **Send output.txt to remote destination via Bluetooth**
- **Sleep 30 seconds and restart service**

![Interface UP](interface_up.gif)
### Receiving scanned results from Raspberry Pi
![Bluetooth android](bluetooth_android.gif)
### Service behavior - Interface DOWN
- **Keeps restarting every 30 seconds indefinitely if no network detected**

![Interface DOWN](interface_down.gif)
### Networkscan program
![Program flow diagram](program_flow_diagram.png)


## Requirements
- **Raspberry Pi 3 or 4**
**(Model 1/2 not tested and bluetooth adapter required)**

- **Python 3.6 or higher**


## Installation
### Linux software setup
Nmap - for scanning network
```console
pi@raspberrypi:~ $ sudo apt-get install python3-nmap -y
```
Bluez-tools - for bluetooth file transfer
```console
pi@raspberrypi:~ $ sudo apt-get install bluetooth bluez-tools -y
```
Git - for cloning repository
```console
pi@raspberrypi:~ $ sudo apt-get install git -y
```
### Networkscan setup
Clone repository
```console
pi@raspberrypi:~ $ git clone https://github.com/tomsozolins/networkscan.git /home/pi/networkscan
```
Navigate to networkscan directory
```console
pi@raspberrypi:~ $ cd /home/pi/networkscan
```
Create virtual environment
```console
pi@raspberrypi:~ $ python3 -m venv venv
```
Activate virtual environment
```console
pi@raspberrypi:~ $ . /home/pi/networkscan/venv/bin/activate
```
Install required python packages
```console
pi@raspberrypi:~ $ pip3 install -r /home/pi/networkscan/requirements.txt
```
### Networkscan service setup
Create networkscan service
```console
pi@raspberrypi:~ $ sudo vi /etc/systemd/system/networkscan.service
```

networkscan.service
```
[Unit]
Description=networkscan service
Requires=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/
ExecStart=/home/pi/networkscan/venv/bin/python3 /home/pi/networkscan/Main.py
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
```
Enable networkscan service at startup
```console
pi@raspberrypi:~ $ sudo systemctl enable networkscan
```

### Bluetooth destination setup
Turn on Bluetooth on your destination device and get its MAC address
```console
pi@raspberrypi:~ $ sudo hcitool scan
```
Example output
```
Scanning ...
        A8:7D:12:51:91:37       HUAWEI P20 lite
```
Modify Bluetooth destination
```console
pi@raspberrypi:~ $ sudo vi /home/pi/networkscan/Main.py
```
Replace MAC_ADDRESS with your destination MAC
```python3
bt-obex -p MAC_ADDRESS /tmp/output.txt
```

## Supported vendors
- **Mobotix AG**
- **Hangzhou Hikvision Digital Technology**
- **Axis Communications AB**
- **Zhejiang Dahua Technology**
- **Panasonic Communications Co**
- **Eaton**

## Author
* **Toms Ozoliņš**

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details