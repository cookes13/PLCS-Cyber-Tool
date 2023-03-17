# Import libaries
import time
import random
import ipaddress
import os
import socket

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

def scanIp(ip):
    ip = '192.168.0.57'
    timeout = 0.1

    for port in range(19, 65536):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((ip, port))
                print(port_to_service(port))
        except:
            pass

def port_to_service(port):
    service_dict = {
        20: 'FTP (File Transfer Protocol)',
        21: 'FTP (File Transfer Protocol)',
        22: 'SSH (Secure Shell)',
        23: 'Telnet',
        25: 'SMTP (Simple Mail Transfer Protocol)',
        53: 'DNS (Domain Name System)',
        80: 'HTTP (Hypertext Transfer Protocol)',
        110: 'POP3 (Post Office Protocol version 3)',
        119: 'NNTP (Network News Transfer Protocol)',
        123: 'NTP (Network Time Protocol)',
        143: 'IMAP (Internet Message Access Protocol)',
        161: 'SNMP (Simple Network Management Protocol)',
        443: 'HTTPS (HTTP Secure)',
        465: 'SMTPS (SMTP Secure)',
        587: 'SMTP (Mail Submission Agent)',
        993: 'IMAPS (IMAP Secure)',
        995: 'POP3S (POP3 Secure)',
        1433: 'Microsoft SQL Server',
        3306: 'MySQL Database',
        5432: 'PostgreSQL Database'
    }


    if port in service_dict:
        return str("Port " + str(port) + ": " + service_dict[port] + " is open")
    else:
        return str("Port " + str(port) + " is open")



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
            scanIp(ip)
        case "3":
            ip1 = input("Enter the start ip >> ")
            ip2 = input("Enter the end ip >> ")
            print (generateIpsRange(ip1, ip2))
        case "4":
            print ("Exiting...")


# Main Code

# print (port_to_service(80))
menu()



