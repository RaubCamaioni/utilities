"""python STRUCT like class for encoding / decoding structs with minimal boiler plate code"""
from io import BytesIO
from collections.abc import Iterable
from dataclasses import Field, dataclass, fields

from typing import get_type_hints, Tuple
from ctypes import sizeof
from enum import Enum

class ENDIAN(Enum):
    LITTLE = -1
    BIG = 1

@dataclass(eq=False)
class CStruct:
    """a simple dataclass to struct format converter (implicit pack 1)"""

    @classmethod
    def size(cls) -> int:
        return sum([sizeof(field.type) for field in fields(cls)]) 
    
    def __setattr__(self, name, value):
        """generic assignment converter for CTYPES"""
        _type = get_type_hints(type(self))[name] # dictionary lookup
        super().__setattr__(name, value if isinstance(value, _type) else (_type(*value) if isinstance(value, Iterable) else _type(value)))

    def to_bytes(self, endian: ENDIAN=ENDIAN.LITTLE):
        """convert Struct to bytes"""

        _values = []
        for field in fields(self):
            # don't reorder strings
            order = 1 if "c_char_Array" in field.type.__name__ else endian.value
            _values.append(bytearray(getattr(self, field.name))[::order])

        return b''.join(_values)

    @classmethod
    def from_bytes(cls, data, endian: ENDIAN=ENDIAN.LITTLE):
        """convert bytes to Struct"""

        if len(data) != cls.size():
            raise ValueError(f"invalid bytes size: class: {cls} input: {len(data)} expected: {cls.size}")

        kwargs = {}
        with BytesIO(data) as stream:
            for field in fields(cls):
                order = 1 if "c_char_Array" in field.type.__name__ else endian.value
                kwargs[field.name] = field.type.from_buffer_copy(stream.read(sizeof(field.type))[::order])

        return cls(**kwargs)

    @classmethod
    def default(cls):
        """assumes ctype default constructor exists"""
        return cls(**{field.name: field.type() for field in fields(cls)})

    def fields(self) -> Tuple[Field, ...]:
        """fields"""
        return fields(self)

    def __str__(self) -> str:
        """formated string representation"""
        data = "\n  ".join([f"{field.name} : {getattr(self, field.name)}" for field in fields(self)])
        return f"{type(self).__name__}\n  {data}"
    
    def line_log(self) -> str:
        return f"{type(self).__name__}: " + ", ".join([f"{getattr(self, field.name).value}" for field in fields(self)])

    def equals(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return all(getattr(self, field1.name).value == getattr(other, field2.name).value for field1, field2 in zip(fields(self), fields(other)))
    
    def __iter__(self):
        return (getattr(self, field.name) for field in fields(self))
