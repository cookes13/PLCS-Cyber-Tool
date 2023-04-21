# Import libaries
import time
import random
import ipaddress
import os
import json
import socket
import threading
import datetime
import platform

# Define functions
def clear():
    os.system('cls' if os.name == 'nt' else 'clear') 

def generateIpsSubnet(subnet):
    # Convert the string to ipaddress object
    subnet = ipaddress.ip_network(str(subnet))
    
    ip_list = []
    for ip in subnet:
        ip_list.append(str(ip))
    return ip_list

def generateIpsRange(start_ip, end_ip):
    # Convert the string to ipaddress object
    start_ip = ipaddress.ip_address(str(start_ip))
    end_ip = ipaddress.ip_address(str(end_ip))

    ip_list = [] # Create an empty list

    # Loop through the range of ip addresses
    for ip in range(int(start_ip), int(end_ip)+1):
        ip_list.append(str(ipaddress.ip_address(ip)))
    return ip_list
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


def portScan(target, start_port=1, end_port=65535):

    # List to keep track of threads and open ports
    threads = []
    ports = []

    def check_port(port):
        thread_id = threading.current_thread().ident
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            sock.connect((target, port))
            ports.append(port)
        except:
            pass
        finally:
            sock.close()

    # Create a thread for each port
    print("Scanning ... Please wait this may take a while")
    for port in range(start_port, end_port+1):
        t = threading.Thread(target=check_port, args=(port,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # All threads have completed
    print("All threads have completed")
    ports.sort()
    print (ports)
    return ports



def port_to_service(port):

    # Read the JSON object from a file
    with open('services.json', 'r') as file:
        port_to_service = json.load(file)

    if str(port) in port_to_service:
        return str("Port " + str(port) + ": " + port_to_service[str(port)] + " is open")
    else:
        return str("Port " + str(port) + ": Unknown is open")



def menu():
    clear()
    print("╔═══════════════════════════════════════╗")
    print("║          1:Scan a Network             ║")
    print("║          2:Scan a Host                ║")
    print("║          3:Scan a IP Range            ║")
    print("║          4:Exit                       ║")
    print("╚═══════════════════════════════════════╝")
    choice = input("Please enter your choice (1-4)>> ")
    match choice:
        case "1":
            subnet = input("Please enter the subnet you want to scan >> ")
        case "2":

            ip = input("Please enter the IP you want to scan >> ")

            openPorts = portScan(ip)
            print("\n\n Open ports:")
            for port in openPorts:
                print(port_to_service(port))
            print("Report Generated: " + generate_port_report(openPorts, ip))

        case "3":
            ip1 = input("Enter the start ip >> ")
            ip2 = input("Enter the end ip >> ")
            print (generateIpsRange(ip1, ip2))
        case "4":
            print ("Exiting...")


# Main Code

# print (port_to_service(80))
menu()



