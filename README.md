# Networkscan
> Raspberry Pi local network device scanner - open port and default password checking for multiple vendors.
### Requirements
Raspberry Pi Model 3 or 4
### Linux software setup
Nmap - for scanning network
```
# sudo apt-get install python3-nmap -y
```
Bluez-tools - for bluetooth file transfer
```
# sudo apt-get install bluez-tools -y
```
Git - for cloning repository
```
# sudo apt-get install git -y
```
### Networkscan software installation
Clone repository
```
# git clone https://github.com/tomsozolins/networkscan.git /home/pi/networkscan
```
Navigate to networkscan directory
```
# cd /home/pi/networkscan
```
Create virtual environment
```
# python3 -m venv venv
```
Activate virtual environment
```
# . /home/pi/networkscan/venv/bin/activate
```
Install required python packages
```
# pip3 install -r /home/pi/networkscan/requirements.txt
```
### Networkscan systemd service setup
Create networkscan service
```
# sudo vi /etc/systemd/system/networkscan.service
```

networkscan.service content
```
[Unit]
Description=networkscan service
Requires=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/
ExecStart=/home/pi/networkscan/venv/bin/python3 /home/pi/networkscan/Main.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```
Enable networkscan service at startup
```
# sudo systemctl enable networkservice
```
## How it works
### Raspberry Pi
![Process flow diagram](process_flow_diagram.png)
### Networkscan program
![Program flow diagram](program_flow_diagram.png)

## Author
* **Toms Ozolins**

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details