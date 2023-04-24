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
            output_str += f"Client: {data['client']}\nPort Range: {data['start_port']}-{data['end_port']}\n\nOpen Ports: {len(data['open_ports'])}\nDuration: {data['duration']}\n------------------------\nOpen Ports:\n"
            for port in data['open_ports']:
                service_name = port_to_service(port)
                output_str += f"    {service_name}\n"
            filename = f"Reports/{service}_{data['client']}_({timestamp}).txt"
        case "network scan":
            output_str += f"Subnet: {data['subnet']}\n\nClients Found: {len(data['online_clients'])}\nDuration: {data['duration']}\n------------------------\nOnline Clients:\n"
            for client in data['online_clients']:
                output_str += f"    {client}\n"
            subnet = str(data['subnet']).replace("/", "_")
            filename = f"Reports/{service}_{subnet}_({timestamp}).txt"
        case "range scan":
            filename = f"Reports/{service}_{data['start_ip']} - {data['end_ip']}_({timestamp}).txt"
            output_str += f"Start Ip: {data['start_ip']}\nEnd Ip:   {data['end_ip']}\n\nClients Found: {len(data['online_clients'])}\nDuration: {data['duration']}\n------------------------\nOnline Clients:\n"
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
def generate_ip_range(start_ip, end_ip):
    try:
        start_ip = ipaddress.IPv4Address(str(start_ip))
        end_ip = ipaddress.IPv4Address(str(end_ip))
    except ValueError:
        return "Error: Invalid IP address"

    # Create a list of all IP addresses in the range
    ip_range = []
    for ip_int in range(int(start_ip), int(end_ip)+1):
        ip_range.append(str(ipaddress.IPv4Address(ip_int)))
    return ip_range
def validate_ip(ip_address):
    if ip_address == "localhost":
        return ip_address
    try:
        ip_address = ipaddress.IPv4Address(ip_address)
        return ip_address
    except ipaddress.AddressValueError:
        return False
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
    
    # Start timing
    start_time = time.time()
    
    # Create a thread for each port
    print(f"Scanning {target} ... Please wait this may take a while")
    for port in range(start_port, end_port+1):
        t = threading.Thread(target=check_port, args=(port,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # End timing
    end_time = time.time()
    time_elapsed_ms = round((end_time - start_time) * 1000)
    time_elapsed_ms = "{:,}".format(time_elapsed_ms)

    ports.sort()
    num_ports = len(ports)
    print(f"{num_ports} ports found in {time_elapsed_ms}ms")
    return ports, time_elapsed_ms
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

    # Start timing
    start_time = time.time()

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

    # End timing
    end_time = time.time()
    time_elapsed_ms = round((end_time - start_time) * 1000)
    time_elapsed_ms = "{:,}".format(time_elapsed_ms)


    return clients, time_elapsed_ms
def scanRange(start_ip, end_ip):
    addresses = generate_ip_range(str(start_ip), str(end_ip))

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
                    clients.append(ip)
                except Exception as e:
                    print(e)
                    print(f"Error: Latency not found for {ip}")

    # Create a list to hold the threads
    clear()
    threads = []
    clients = []

    # Start timing
    start_time = time.time()

    count=0
    for address in addresses:
        count+=1

    print(f"Scanning {count} addresses ... Please wait this may take a while")
    # Start a thread for each IP address in the range
    for ip in addresses:
        thread = threading.Thread(target=ping_ip, args=(ip,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


    # End timing
    end_time = time.time()
    time_elapsed_ms = round((end_time - start_time) * 1000)
    time_elapsed_ms = "{:,}".format(time_elapsed_ms)

    return clients, time_elapsed_ms


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
                
            duration = clients[1]
            clients = clients[0]

            print("Generating Report ...")
            data = {
                "subnet": subnet,
                "online_clients": clients,
                "duration": f"{duration} ms"
            }
            reportFile = generate_report('Network Scan', data)
            print(f"Report written to {reportFile}")
            input("Press {Enter} to Continue  ")
            menu()

        case "2":
            while True:
                ip = validate_ip(input("Please enter the IP you want to scan >> "))
                if ip == False:
                    print("Error: Invalid IP Address")
                else:
                    break
            openPorts = portScan(ip)
            duration = openPorts[1]
            openPorts = openPorts[0]
            print("Generating Report ...")
            time.sleep(5)
            clear()
            data = {
                "client": ip,
                "start_port": 1,
                "end_port": 65535,
                "duration": f"{duration} ms",
                "open_ports": openPorts
            }
            reportFile = generate_report("Port Scan", data)
            print(f"Report written to {reportFile}")
            input("Press {Enter} to Continue  ")
            menu()
        case "3":
            while True:
                ip1 = input("Enter the start ip >> ")
                ip2 = input("Enter the end ip >> ")
                clients = scanRange(ip1, ip2)
                if "Error" in clients:
                    print(clients)
                else:
                    break
            duration = clients[1]
            clients = clients[0]

            print("Generating Report ...")
            data = {
                "start_ip": ip1,
                "end_ip": ip2,
                "online_clients": clients,
                "duration": f"{duration} ms"
            }
            reportFile = generate_report("Range Scan", data)
            print(f"Report written to {reportFile}")
            input("Press {Enter} to Continue  ")
            menu()
        case "4":
            print ("Exiting...")
            time.sleep(1)
            quit()
        case _:
            print("Error: Invalid choice")
            time.sleep(0.5)
            menu()

menu()



