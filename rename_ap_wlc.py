import requests
import json
import getpass
import os
import re

#The first line of the text file that contains the AP information should be one of these:
#NEW_NAME WTP_MAC
#NEW_NAME OLD_NAME
#NEW_NAME ETH_MAC
requests.packages.urllib3.disable_warnings() 

current_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(current_dir, 'ap_info.txt')
WLC_IP="10.192.3.211"

def change_ap_name(new_ap_name,old_ap_name,ap_mac_addr,change_by_name_or_mac):
    
    url = "https://" + WLC_IP + "/restconf/data/Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-name"


    if(change_by_name_or_mac == 0):
        payload = json.dumps({
        "Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-name": {
            "name": new_ap_name,
            "mac-addr": ap_mac_addr
        }
        })
    elif(change_by_name_or_mac == 1):
        payload = json.dumps({
        "Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-name": {
            "name": new_ap_name,
            "ap-name": old_ap_name
        }
        })
    else:
        raise Exception(str(change_by_name_or_mac) + " is not a valid option.Please select 0 for changing using the MAC address or 1 for changing using the old AP name")

    headers = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json',
    }

    with requests.Session() as session:
        response = session.request("POST", url, headers=headers,data=payload,auth=(username,password),verify=False)

        if("ietf-restconf:errors" in response.text):
            print("AP name change for " + old_ap_name +  "failed!" + response.text.replace("\n", ""))
        else:
            print("AP name was changed from "+ old_ap_name + " to " + new_ap_name)

    
    



with open(filename,'r') as f:
        ap_names_file = f.readlines()
        
#Remove trailing newlines and empty elements
for i in range(len(ap_names_file)):
    ap_names_file[i]=ap_names_file[i].rstrip()
ap_names_file=list(filter(None,ap_names_file))

data_type=ap_names_file[0].split(" ")[0] + "->" + ap_names_file[0].split(" ")[1]

del ap_names_file[0]

username = input("Enter username:")
password = getpass.getpass(prompt="Enter password:")

url = "https://" + WLC_IP + "/restconf/data/Cisco-IOS-XE-wireless-ap-global-oper:ap-global-oper-data/ap-join-stats"

payload = {}
headers = {
  'Accept': 'application/yang-data+json',
  'Content-Type': 'application/yang-data+json',
}


with requests.Session() as s:

    response = s.request("GET", url, headers=headers, auth=(username,password),verify=False)

    ap_dict = json.loads(response.text)

    if("ietf-restconf:errors" in ap_dict):
         raise Exception("Failed login!" + response.text)

    for i in range(len(ap_dict["Cisco-IOS-XE-wireless-ap-global-oper:ap-join-stats"])):
        
        ap_name = ap_dict["Cisco-IOS-XE-wireless-ap-global-oper:ap-join-stats"][i]["ap-join-info"]["ap-name"]
        ap_mac = ap_dict["Cisco-IOS-XE-wireless-ap-global-oper:ap-join-stats"][i]["wtp-mac"]
        is_ap_joined=ap_dict["Cisco-IOS-XE-wireless-ap-global-oper:ap-join-stats"][i]["ap-join-info"]["is-joined"]
        ap_eth_mac=ap_dict["Cisco-IOS-XE-wireless-ap-global-oper:ap-join-stats"][i]["ap-join-info"]["ap-ethernet-mac"]

        #Check if AP is joined, name change doesn't work for un-joined APs
        if(is_ap_joined):

            if(data_type=="NEW_NAME->WTP_MAC"):
                for index in range(len(ap_names_file)):
                    if(ap_names_file[index].split(" ")[1].lower() == ap_mac.lower() and ap_names_file[index].split(" ")[0].lower()!=ap_name.lower()):
                        change_ap_name(ap_names_file[index].split(" ")[0],ap_name.lower(),ap_mac.lower(),0)
            
            elif(data_type=="NEW_NAME->OLD_NAME"):
                for index in range(len(ap_names_file)):
                    if(ap_names_file[index].split(" ")[1].lower() == ap_name.lower() and ap_names_file[index].split(" ")[0].lower()!=ap_name.lower()):
                        change_ap_name(ap_names_file[index].split(" ")[0],ap_name.lower(),ap_mac.lower(),1)
                
            elif(data_type=="NEW_NAME->ETH_MAC"):       
                for index in range(len(ap_names_file)):
                    if(ap_names_file[index].split(" ")[1].lower() == ap_eth_mac.lower() and ap_names_file[index].split(" ")[0].lower()!=ap_name.lower()):
                        change_ap_name(ap_names_file[index].split(" ")[0],ap_name.lower(),ap_mac.lower(),0)