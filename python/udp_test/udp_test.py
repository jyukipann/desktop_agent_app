import socket
from multiprocessing import Process
import asyncio
import json

class server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 6200
        self.ip = "127.0.0.1"
        self.addr = (self.ip,self.port)
        self.socket.bind(self.addr)
        self.socket.getblocking()
        self.is_waiting = False
        self.bytes, self.src_addr = None, None
        self.received_data = None
        self.loop = None

    async def receive(self):
        self.bytes, self.src_addr = self.socket.recvfrom(4092)
        str_data = self.bytes.decode("utf-8")
        return json.loads(str_data)

    def wait_recive(self):
        self.is_waiting = True
        self.loop = asyncio.get_event_loop()
        while(self.is_waiting):
            self.received_data = self.loop.run_until_complete(self.receive())
            print(f"received : {self.received_data}")

    def stop_waiting(self):
        self.is_waiting = False
        if(self.loop is not None):
            self.loop.close()
        self.socket.close()

class client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 6200
        self.ip = "127.0.0.1"
        self.addr = (self.ip,self.port)

    def send(self, data:dict):
        json_data = json.dumps(data)
        self.socket.sendto(json_data.encode("utf-8"), self.addr)

    def close(self):
        self.socket.close()

def server_side():
    srv = server()
    srv.wait_recive()
    srv.stop_waiting()

def client_side():
    clt = client()
    print("waiting")
    data = {}
    while True:
        try:
            data[0] = input("send what? : ")
            clt.send(data)
        except KeyboardInterrupt:
            break
    clt.close()

if __name__ == "__main__":
    server_side_process = Process(target=server_side)
    server_side_process.daemon = True
    server_side_process.start()
    client_side()
    server_side_process.terminate()

