from multicast import MulticastComm
from argparse import ArgumentParser
import time

def listen(address, rport, interface):

    multicastComm = MulticastComm(address, rport, rport, interface)
    multicastComm.observers.append(lambda d: print(d))
    multicastComm.connect()
    multicastComm.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        multicastComm.stop()

def sender(address, sport, interface, data):
    multicastComm = MulticastComm(address, sport, sport, interface)
    multicastComm.connect()
    multicastComm.send_data(data)

if __name__ == "__main__":

    parser = ArgumentParser(prog="MulticastCapture")
    parser.add_argument("-m", "--mode", type=int, default=0)
    parser.add_argument("-a", "--address", type=str)
    parser.add_argument("-p", "--port", type=int)
    parser.add_argument("-i", "--interface", default="0.0.0.0", type=str)
    parser.add_argument("-d", "--data", default="", type=str)
    args = parser.parse_args()

    print(f"Multicast {'Listening' if args.mode==0 else 'Sending'}")
    print(f"mode: {args.mode}")
    print(f"address: {args.address}")
    print(f"port: {args.port}")
    print(f"interface: {args.interface}")

    if args.mode == 0:
        listen(args.address, args.port, args.interface)
    else:
        sender(args.address, args.port, args.interface, data)