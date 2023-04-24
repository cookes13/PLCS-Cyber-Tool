import ipaddress

def generate_subnet(ip, mask):
    ip = verifyIP(ip)
    subnet = ipaddress.IPv4Network(str(ip) + mask, strict=False)
    return subnet

def verifyIP(ip):
    try:
        ip = ipaddress.IPv4Address(str(ip))
        return ip
    except Exception as e:
        return f"Error: {e}"
    
def is_valid_ip(ip_address):
    try:
        ip_address = ipaddress.IPv4Address(ip_address)
        return ip_address
    except ipaddress.AddressValueError:
        return False

while True:
    ip = input("Enter IP address >> ")
    print(f"{is_valid_ip(ip)} is valid IP address. Var Type{type(is_valid_ip(ip))}")



