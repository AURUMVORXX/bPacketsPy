import g2o
import inspect
from .btypes import *

packetHandlers = dict()

class BPacketMessageMeta(type):
    def __new__(mcs, name, bases, attrs):
        
        # Generating unique ID for each packet based on its name, basically bitshifting all the symbols (lowercase and uppercase) and fit it into 32 bit int
        attrs['_id'] = 1
        for x in name:
            attrs['_id'] = ((ord(x) << 16) | (ord(x.upper()) >> 16)) ^ attrs['_id']
        
        return super().__new__(mcs, name, bases, attrs)
        
class BPacketMessage(metaclass=BPacketMessageMeta):
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
            
    def serialize(self):
        
        packet = g2o.Packet()
        
        # Writing header (ID)
        packet.writeInt32(self.id)
        
        # Getting all class properties, which is not hidden (starts with _) and not methods
        properties = [name for (name, value) in inspect.getmembers(self) if not name.startswith('_') and not callable(value)]
        properties.sort()
        
        # Iterating through all properties, getting specified type from annotations (property : TYPE) and write into packet
        for key in properties:
            data_type   = self.__annotations__[key] if ('__annotations__' in inspect.getmembers(self) and key in self.__annotations__) else BPacketAny
            data        = self.__getattribute__(key)
            data_type.write(packet, data)
            
        return packet
    
    @classmethod
    def deserialize(cls, packet):
        message = cls()
        
        properties = [name for (name, value) in inspect.getmembers(message) if not name.startswith('_') and not callable(value)]
        properties.sort()
        for key in properties:
            data_type   = message.__annotations__[key] if ('__annotations__' in inspect.getmembers(message) and key in message.__annotations__) else BPacketAny
            message.__setattr__(key, data_type.read(packet))
            
        return message
    
    @classmethod
    def bind(cls, func):
        packetHandlers[cls.id] = {'class': cls, 'func': func}
        
@g2o.event('onPacket')
def evtPacket(**kwargs):
    pid     = kwargs['playerid']
    packet  = kwargs['data']
    
    header = packet.readUInt32()
    if (header in packetHandlers):
        message = packetHandlers[header]['class'].deserialize(packet)
        packetHandlers[header]['func'](pid, message)