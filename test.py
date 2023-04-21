import threading
import socket

def portScan(target="localhost", start_port=1, end_port=65535):

    # List to keep track of threads
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
    print("Scanning ...")
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
    return ports

openPorts = portScan()
print("\n\n Open ports:")
print(openPorts)