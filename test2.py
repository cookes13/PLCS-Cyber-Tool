import ipaddress

def generate_subnet(ip, mask):
    ip = ipaddress.IPv4Address(str(ip))
    subnet = ipaddress.IPv4Network(str(ip) + mask, strict=False)
    return subnet

print(generate_subnet("192.168.0.25", "/24"))
