import argparse, sys, socket # Import all
from threading import Thread
import json
# We use threading, cuz multiprocessing is bad at passing arguments to targets
# also, we don`t need GIL unlocking.

VERSION = "v0.2"

class Client:
    def __init__(self):
        
        self.parser()
        self.start()


    def build_msg(self, msg): # Build msg
        message = {"user": "[BRIDGE]", "msg": msg}                    
        return json.dumps(message, ensure_ascii=False).encode()


    def parser(self): 
        parser = argparse.ArgumentParser(
        prog="anonchat-bridge",
        description = "Bridge messages between two anonchats",
        epilog="---- Oh, hello there!") # Create parser
 
        parser.add_argument("ip", help = "IP of first anonchat-server", type=str)
        parser.add_argument("ip2", help = "IP of second anonchat-server", type=str) # Assign all args
        
        args = parser.parse_args() # Parse args

        ip = args.ip.split(":") # Split First IP
        ip.append(6969) # If port is not passed, add it to select later

        ip2 = args.ip2.split(":") # Second IP
        ip2.append(6969)

        if ip == ip2:
            print(f"Cannot bridge two same servers!")
            sys.exit()

        self.ip = ip[0] # Select First IP adress
        try:
            self.port = int(ip[1]) # Try to parse port
        except:
            print(f"Cannot parse port {ip[1]} as number. Aborting.")
            sys.exit()

        self.ip2 = ip2[0] # Second IP
        try:
            self.port2 = int(ip2[1]) # Second port
        except:
            print(f"Cannot parse port {ip2[1]} as number. Aborting.")
            sys.exit()

    def start(self):
        print(f"[BRIDGE] [GEN] [INF] Bridge version - {VERSION}")
        print(f"[BRIDGE] [GEN] [INF] Connecting Socket to IP0 - {self.ip}:{self.port}")
        self.socket_ip1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create and bind first socket to First IP
        self.socket_ip1.connect((self.ip, self.port))
        print(f"[BRIDGE] [GEN] [INF] Socket bound to IP0")

        print(f"[BRIDGE] [GEN] [INF] Connecting Socket to IP1 - {self.ip2}:{self.port2}")
        self.socket_ip2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Second IP
        self.socket_ip2.connect((self.ip2, self.port2))
        print(f"[BRIDGE] [GEN] [INF] Socket bound to IP1")

        self.socket_ip1.send(self.build_msg(f"Bridge from {self.ip2}:{self.port2} bounded to this server!"))
        self.socket_ip2.send(self.build_msg(f"Bridge from {self.ip}:{self.port} bounded to this server!"))
        message_blacklist = [self.build_msg(f"Bridge from {self.ip}:{self.port} bounded to this server!"),
                             self.build_msg(f"Bridge from {self.ip2}:{self.port2} bounded to this server!")]
        
        print(f"[BRIDGE] [GEN] [INF] Start up all processes...")
        self.prc_pipe = {"1": None, "2": None, "blacklist": message_blacklist, "kill": False} # Target last messages, or it will create a bunch of spam
        self.request_1 = Thread(target=self.bridge_to, args=(self.socket_ip1, self.socket_ip2, self.prc_pipe, "1"), daemon=True) # Create Thread to send messages from First IP to Second
        self.request_1.start()

        self.request_2 = Thread(target=self.bridge_to, args=(self.socket_ip2, self.socket_ip1, self.prc_pipe, "2"), daemon=True) # From Second To First
        self.request_2.start()

            
        while True:
            pass

    def bridge_to(self, socket1, socket2, info, num): # First Socket (to listen from), Second Socket (to send messages), dict with last messages, num of server
        target_num = [x for x in info if x != num and x.isdigit()][0]

        while True:
            if info["kill"]:
                return
            
            try:
                message = socket1.recv(1024) # Receive message from
            except:
                break # Break process if error
                
            if not message: # If no message, break all process
                break
            
            print(f"[BRIDGE] [IP{int(num)-1}] [INF] Got message from IP{int(num)-1}!")

            if info[num] != message and not message in info["blacklist"]: # If message is was not sended in this server at last
                print(f"[BRIDGE] [IP{int(num)-1}] [INF] Sending message to IP{int(target_num)-1}.")
                socket2.send(message) # Send encoded message
                info.update({"1": message}) # Set up last messages at 1 and at second server
                info.update({"2": message})
            else:
                print(f"[BRIDGE] [IP{int(num)-1}] [INF] Not sending message, because message is already sended or in blacklist.")

if __name__ == "__main__":
    cli = Client() # Create object if not imported
        
