# Rename APs using RESTCONF in bulk
The script modifies the Access Point names in bulk using a txt file. Based on the first line of the file it will either try to find them based on the AP MAC Address, the AP Ethernet Port MAC Address or the old AP name(use files in the templates directory).
It gets all the AP information from the WLC via a RESTAPI call then tries to find them in the ap_info.txt file based on the criteria described above. Once found it checks if the name defined in the file is different then proceeds to rename it via another RESTAPI call.
