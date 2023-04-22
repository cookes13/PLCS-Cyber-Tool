# Import libaries
import time
import ipaddress
import os
import json
import socket
import threading
import datetime
import platform
import subprocess
import re

# Utility functions
def clear():
    os.system('cls' if os.name == 'nt' else 'clear') 
def center_text(text, length):
    if len(text) >= length:
        # If the text is already at least as long as the target length,
        # simply return the original text.
        return text
    # Calculate the number of spaces needed on each side of the text to center it.
    num_spaces = length - len(text)
    left_spaces = num_spaces // 2
    right_spaces = num_spaces - left_spaces   
    # Add the necessary spaces to the beginning and end of the text.
    centered_text = ' ' * left_spaces + text + ' ' * right_spaces
    return centered_text
def port_to_service(port):
    # Read the JSON object from a file
    with open('services.json', 'r') as file:
        port_to_service = json.load(file)

    if str(port) in port_to_service:
        return str("Port " + str(port) + ": " + port_to_service[str(port)] + " is open")
    else:
        return str("Port " + str(port) + ": Unknown is open")
def generate_report(service,data):
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' UTC'
    
    # Get host netname and username
    host = str(platform.node())
    user = str(os.getlogin())
    

    output_str = f"Timestamp: {timestamp}\nHost: {host}\nUser: {user}\n----------------------------------------\n{center_text(service,40)}\n----------------------------------------\n"
    timestamp = timestamp.replace(":", "-")

    match service.lower():
        case "port scan":
            output_str += f"Client: {data['client']}\nPort Range: {data['start_port']}-{data['end_port']}\n------------------------\nOpen Ports:\n"
            for port in data['open_ports']:
                service_name = port_to_service(port)
                output_str += f"    {service_name}\n"
            filename = f"Reports/{service}_{data['client']}_({timestamp}).txt"
        case "network scan":
            output_str += f"Subnet: {data['subnet']}\n------------------------\nOnline Clients:\n"
            for client in data['online_clients']:
                output_str += f"    {client}\n"
            subnet = str(data['subnet']).replace("/", "_")
            filename = f"Reports/{service}_{subnet}_({timestamp}).txt"
        case "ip range":
            output_str += f"Start Ip: {data['start_ip']}\nEnd Ip: {data['end_ip']}\n------------------------\nOnline Clients:\n"
            for client in data['online_clients']:
                output_str += f"    {client}\n"
    
    file = open(filename, "w")
    file.write(output_str)
    file.close()
    clear()
    print(output_str)
    return filename
def generate_subnet(ip, mask=""):
    if "/" in ip:
        mask = str("/" + ip.split("/")[1])
        ip = str(ip.split("/")[0])
    if mask == "":
        mask = "/24"
    try:
        ip = ipaddress.IPv4Address(str(ip))
    except ValueError:
        return "Error: Invalid IP address"
    
    subnet = ipaddress.IPv4Network(str(ip) + mask, strict=False)
    return subnet


# Scanners
def portScan(target, start_port=1, end_port=65535):
    clear()
    lock = threading.Lock()
    def outputPort(port):
        with lock:
            print(f"Port {port} is open")
    def check_port(port):  
        thread_id = threading.current_thread().ident
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            sock.connect((target, port))
            ports.append(port)
            outputPort(port)
        except:
            pass
        finally:
            sock.close()
    # List to keep track of threads and open ports
    threads = []
    ports = []
    # Create a thread for each port
    print(f"Scanning {target} ... Please wait this may take a while")
    for port in range(start_port, end_port+1):
        t = threading.Thread(target=check_port, args=(port,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()
    ports.sort()
    return ports
def scanNetwork(network_subnet):
    # Parse the IP range into a network object
    try:
        network = ipaddress.ip_network(network_subnet)
    except ValueError:
        return "Error: Invalid network address"

    # Determine the appropriate ping command and flags for the current operating system
    if platform.system() == "Windows":
        ping_cmd = "ping"
        ping_flags = "-n 1 -w 500"
        latency_pattern = r"Average = (\d+)ms"
    else:
        ping_cmd = "ping"
        ping_flags = "-c1 -W 100"
        latency_pattern = r"time=(\d+\.\d+)"

    # Create a lock to synchronize thread output
    lock = threading.Lock()

    # Define a function to ping an IP address
    def ping_ip(ip):
        # Use the ping command to ping the IP address
        cmd = f"{ping_cmd} {ping_flags} {ip}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Extract the latency from the output using a regular expression
        latency_match = re.search(latency_pattern, result.stdout)
        
        # Print the result and the latency using the lock to synchronize output
        with lock:
            if result.returncode == 0:
                try:
                    print(f"{ip} is up! Latency: {latency_match.group(1)} ms")
                    clients.append(ip.exploded)
                except:
                    print(f"Error: Latency not found for {ip}")

    # Create a list to hold the threads
    clear()
    threads = []
    clients = []

    count=0
    for address in network:
        count+=1

    print(f"Scanning {count} addresses ... Please wait this may take a while")
    # Start a thread for each IP address in the range
    for ip in network:
        thread = threading.Thread(target=ping_ip, args=(ip,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    return clients


def menu():
    clear()
    print("╔═══════════════════════════════════════╗")
    print("║          1:Scan a Network             ║")
    print("║          2:Port Scan                  ║")
    print("║          3:Scan a IP Range            ║")
    print("║          4:Exit                       ║")
    print("╚═══════════════════════════════════════╝")
    choice = input("Please enter your choice (1-4)>> ")
    match choice:
        case "1":
            while True:
                subnet = input("Please enter the subnet you want to scan >> ")
                if "/" not in subnet:
                    print(f"Error: Invalid subnet, network mask is missing (e.g.{subnet}/24)")
                    continue
                subnet = generate_subnet(subnet)
                clients = scanNetwork(subnet)
                if "Error" in clients:
                    print(clients)
                else:
                    break

            print("Generating Report ...")
            data = {
                "subnet": subnet,
                "online_clients": clients
            }
            generate_report("Network Scan", data)
        case "2":
            ip = input("Please enter the IP you want to scan >> ")
            openPorts = portScan(ip)
            print("Generating Report ...")
            time.sleep(1)
            clear()
            data = {
                "client": ip,
                "start_port": 1,
                "end_port": 65535,
                "open_ports": openPorts
            }
            generate_report("Port Scan", data)

        case "3":
            ip1 = input("Enter the start ip >> ")
            ip2 = input("Enter the end ip >> ")
            # print (generateIpsRange(ip1, ip2))
        case "4":
            print ("Exiting...")

menu()



