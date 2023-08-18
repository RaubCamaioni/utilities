import time
from functools import partial
from contextlib import suppress
from multicast_thread import MulticastThread

def OneWayBridge(input_address, input_port, input_interface, output_address, output_port, output_interface):

    inputMulticast = MulticastListener(input_address, input_port, input_interface)
    outputMulticast = MulticastListener(output_address, output_port, output_interface)

    def filtered_send(listener: MulticastListener, interface, data, server):
        address, port = interface

        if address == interface:
            return

        if address.split('.')[:2] == listener.network_adapter.split('.')[:2]:
            return

        listener.send(data)

    inputMulticast.add_observer(partial(filtered_send, outputMulticast, input_interface))
    outputMulticast.add_observer(partial(filtered_send, inputMulticast, output_interface))

    inputMulticast.start()
    outputMulticast.start()

    with suppress(KeyboardInterrupt):
        while True: time.sleep(60*24)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PyBridge Network Settings")
    parser.add_argument("-i", "--input", help="input address:port:interface", required=True)
    parser.add_argument("-o", "--output", help="output address:port:interface", required=True)
    args = parser.parse_args()

    print("PyBridge:")
    print(f"Bridge1: (address, port, interface): {tuple(args.input.split(':'))}")
    print(f"Bridge2: (address, port, interface): {tuple(args.output.split(':'))}")
    OneWayBridge(*args.input.split(':'), *args.output.split(':'))