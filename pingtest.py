import ipaddress
import threading
import subprocess
import platform
import re
import socket

def scanNetwork(ip_range):
    # Parse the IP range into a network object
    network = ipaddress.ip_network(ip_range)

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
                except:
                    print(f"Error: Latency not found for {ip}")

    # Create a list to hold the threads
    threads = []

    # Start a thread for each IP address in the range
    for ip in network:
        thread = threading.Thread(target=ping_ip, args=(ip,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


ping_ip_range("192.168.0.0/24")
