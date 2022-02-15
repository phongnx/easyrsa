#!/usr/bin/env python3
import json
import re
import time

import requests


class CountUser:
    last_user = 0
    max_current_connection = 0
    vpn_type = 1

    def read_config(self):
        file = open("/etc/openvpn/server.conf", "r")
        for lines in file:
            if re.match("duplicate-cn", lines):
                self.vpn_type = 0
            if lines.startswith("max-clients"):
                self.max_current_connection = lines.split()[1]

    def push_new_vpn_to_dash_broad(self, b, list):
        self.read_config()
        r = requests.get("https://ipinfo.io/json")
        print(r.text)
        data_from_ip_info = json.loads(r.text)
        id_vps = str(data_from_ip_info["ip"]).replace(".", "")
        result_data = {
            'id': id_vps,
            'host_name': "vpn" + str(id_vps),
            'ip': str(data_from_ip_info["ip"]),
            'current_connection': b,
            'max_connection': self.max_current_connection,
            'city': str(data_from_ip_info["city"]),
            'region': str(data_from_ip_info["region"]),
            'country': str(data_from_ip_info["country"]),
            'vpn_type': self.vpn_type,
            'users_connected': json.dumps(list)
        }
        print(result_data)
        var = requests.post("http://50.116.8.251/api/creatVpn", data=result_data)
        print(var.text)

    def print_time(self):
        fd = open("/var/log/openvpn/status.log", "r")
        b = 0
        list_user = []
        for lines in fd:
            if re.match("ROUTING TABLE", lines):
                b = b - 3
                if b != self.last_user:
                    self.last_user = b
                r = requests.get("https://api.ipify.org")
                print(r.text)
                print(list_user)
                name = r.text.replace(".", "")
                pload = {'id': name, 'current_connection': b, 'users_connected': json.dumps(list)}
                print(pload)
                path = "http://50.116.8.251/api/updateNumberConnect"
                data = requests.post(path, data=pload)
                print(data.text)
                data_from_ip_info = json.loads(r.text)
                error = data_from_ip_info["error"]
                if re.match("201", error):
                    self.push_new_vpn_to_dash_broad(b, list_user)

                break
            else:
                list_user.append(lines)
                b = b + 1

    def run(self):
        while True:
            time.sleep(5)
            # file = Path("/var/log/openvpn/status.log")
            # if file.is_file():
            try:
                self.print_time()
            except:
                continue
            # else:
            #     break


CountUser().run()
