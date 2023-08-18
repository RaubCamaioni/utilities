import time 
import socket 
import platform
from threading import Thread, Lock

from queue import Queue, Full
from contextlib import suppress
from typing import Callable, Union
from ipaddress import ip_network, ip_address

class MulticastThread(Thread):

    def __init__(self, address: str, rport: int, sport: int, network_adapter: str):
        Thread.__init__(self)

        self.t = time.time()
        self.address = address
        self.rport = rport
        self.sport = sport
        self.network_adapter = network_adapter

        self.running = False
        self.queue: Queue[bytes] = Queue(maxsize=100)
        self.observers: list[Callable[[bytes], None]] = []

        # sending lock 
        self.send_lock = Lock()

        # single socket for windows and linux
        self.sock: Union[socket.socket, None] = None

    def connect(self):
        self.sock = self._connect(self.rport)

    def _connect(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)

        # check if we are using a multicast address
        if ip_address(self.address) in ip_network("224.0.0.0/4"):

            # very unpythonic looking code, essentially a switch case inside a dictionary format
            # probably very slow compared to if statements
            {
                "Linux":   lambda: sock.bind((self.address,         port)),
                "Windows": lambda: sock.bind((self.network_adapter, port))
            }.get(platform.system(), lambda: SystemError("unsupported system"))()
                
            # set multicast output interface, join multicast group
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.network_adapter))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.address) + socket.inet_aton(self.network_adapter))

        else:

            # udp binds directly to interface
            sock.bind((self.network_adapter, port))

        return sock

    def run(self):
        assert self.sock is not None
        
        self.running = True

        # signal thread, de-couple multicast receival from observer processing
        _signal_thread = Thread(target=self.signal_thread, daemon=True)
        _signal_thread.start()

        while self.running:

            try:
                data, server = self.sock.recvfrom(2 ** 20)
                self.queue.put(data, block=True, timeout=.1)
            except socket.timeout:
                continue
            except Full:
                print("multicast queue full dropping data: observer might be hanging signal thread")

        self.sock.close()

    def signal_thread(self):
        while self.running:
            data = self.queue.get()
            self.signal(data)

    def send_data(self, message: bytes):
        assert self.sock is not None

        # aquire lock and send data
        with self.send_lock:
            d = time.time() - self.t
            if d < .1: time.sleep(d)
            self.t = time.time()
            self.sock.sendto(message, (self.address, self.sport))

    def __enter__(self):
        self.connect()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self):
        self.running = False
        self.join()

    def signal(self, data):
        [obs(data) for obs in self.observers]
