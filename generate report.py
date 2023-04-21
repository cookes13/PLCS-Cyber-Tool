import datetime
import json
import platform
import os




port_list = [80, 135, 443, 445, 808, 1337, 3306, 5040, 5146, 5354, 5426, 5563, 5939, 7865, 13333, 13339, 13340, 13344, 27015, 27275, 49664, 49665, 49666, 49667, 49668, 49669, 49695, 49696, 49780, 49781, 49812, 49933, 54235, 54236, 55000, 61778, 61779, 65001]

def generate_port_report(port_list, client):
    # Get current timestamp
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' UTC'
    
    # Get host netname and username
    host = str(platform.node())  # Replace with actual host netname
    user = str(os.getlogin())  # Replace with actual username
    
    # Generate report header
    report = f"Timestamp: {timestamp}\nHost: {host}\nUser: {user}\n---------------------\nClient: {client}\nPort Range: 1-65535\n------------------------\nOpen Ports\n"
    
    # Generate report body
    for port in port_list:
        service_name = port_to_service(port)
        report += f"    {service_name}\n"

    timestamp = timestamp.replace(":", "-")
    filename = f"Reports/report_{client}_({timestamp}).txt"
    file = open(filename, "w")
    file.write(report)
    file.close()
    return filename

print(generate_port_report(port_list, client))

def port_to_service(port):

    # Read the JSON object from a file
    with open('services.json', 'r') as file:
        port_to_service = json.load(file)

    if str(port) in port_to_service:
        return str("Port " + str(port) + ": " + port_to_service[str(port)] + " is open")
    else:
        return str("Port " + str(port) + ": Unknown is open")
    
client="192.168.0.57"

