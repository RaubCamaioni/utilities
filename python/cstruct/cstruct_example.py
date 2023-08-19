from cstruct import CStruct
from ctypes import *
from dataclasses import dataclass

# example message constructions
# dataclass decorator is required
# all dataclass fields must be ctypes

@dataclass
class Header(CStruct):
    id: c_char * 25
    timestamp: c_double
    message_type: c_uint32

@dataclass    
class MessageTypeA(Header):
    message_data_a: c_char * 10
    
if __name__ == "__main__":
    
    from time import time
    
    # create header struct    
    header = Header(b"Hello World", time(), 69)    
    header_bytes = header.to_bytes()
    
    print(f"originial:{header}")
    print(f"bytes: {header_bytes}")
    print(f"reconstruct: {Header.from_bytes(header_bytes)}\n")
    
    # create message type with header struct
    header.timestamp = time()
    messageA = MessageTypeA(*header, b"MessageA")
    messageA_bytes = messageA.to_bytes()
    
    print(f"originial:{messageA}")
    print(f"bytes: {messageA_bytes}")
    print(f"reconstruct: {MessageTypeA.from_bytes(messageA_bytes)}\n")
    
    # parse only header
    header = Header.from_bytes(messageA_bytes[:Header.size()])
    print(header, '\n')
    
    # everything is a ctype, to get the python represented value use ctype.value
    print(header.id.value, '\n')
    
    # single line print function given, you can edit the __str__ to print ctypes.value vs ctypes
    print(messageA.line_log())


