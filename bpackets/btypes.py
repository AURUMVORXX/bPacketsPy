from enum import IntEnum, auto

class BPacketInt8:
    
    @staticmethod
    def write(packet, value):
        packet.writeInt8(value)
        
    @staticmethod
    def read(packet):
        return packet.readInt8()

class BPacketInt16:
    @staticmethod
    def write(packet, value):
        packet.writeInt16(value)
        
    @staticmethod
    def read(packet):
        return packet.readInt16()

class BPacketInt32:
    
    @staticmethod
    def write(packet, value):
        packet.writeInt32(value)
        
    @staticmethod
    def read(packet):
        return packet.readInt32()

class BPacketUInt8:
    
    @staticmethod
    def write(packet, value):
        packet.writeUInt8(value)
        
    @staticmethod
    def read(packet):
        return packet.readUInt8()

class BPacketUInt16:
    
    @staticmethod
    def write(packet, value):
        packet.writeUInt16(value)
        
    @staticmethod
    def read(packet):
        return packet.readUInt16()

class BPacketUInt32:
    
    @staticmethod
    def write(packet, value):
        packet.writeUInt32(value)
        
    @staticmethod
    def read(packet):
        return packet.readUInt32()
        
class BPacketString:
    
    @staticmethod
    def write(packet, value):
        packet.writeString(value)
        
    @staticmethod
    def read(packet):
        return packet.readString()
        
class BPacketFloat:
    
    @staticmethod
    def write(packet, value):
        packet.writeFloat(value)
        
    @staticmethod
    def read(packet):
        return packet.readFloat()
    
class BPacketBool:
    
    @staticmethod
    def write(packet, value):
        packet.writeBool(value)
        
    @staticmethod
    def read(packet):
        return packet.readBool()
        
class BPacketAnyType(IntEnum):
    NULL    = 0
    BOOL    = auto()
    INT8    = auto()
    UINT8   = auto()
    INT16   = auto()
    UINT16  = auto()
    INT32   = auto()
    FLOAT   = auto()
    STRING  = auto()
    ARRAY   = auto()
    TABLE   = auto()
    
class BPacketAny:
    
    @staticmethod
    def write(packet, value):
        
        value_type = type(value)
        
        if (value is None):
            packet.writeUInt8(BPacketAnyType.NULL)
            
        elif (value_type == bool):
            packet.writeUInt8(BPacketAnyType.BOOL)
            packet.writeBool(value)
            
        elif (value_type == int):
            if (value >= -128 and value <= 127):
                packet.writeUInt8(BPacketAnyType.INT8)
                packet.writeInt8(value)
            elif (value >= 0 and value <= 255):
                packet.writeUInt8(BPacketAnyType.UINT8)
                packet.writeInt8(value)
            elif (value >= -32768 and value <= 32767):
                packet.writeUInt8(BPacketAnyType.INT16)
                packet.writeInt8(value)
            elif (value >= 0 and value <= 65535):
                packet.writeUInt8(BPacketAnyType.UINT16)
                packet.writeInt8(value)
            else:
                packet.writeUInt8(BPacketAnyType.INT32)
                packet.writeInt32(value)
        
        elif (value_type == float):
            packet.writeUInt8(BPacketAnyType.FLOAT)
            packet.writeFloat(value)
            
        elif (value_type == str):
            packet.writeUInt8(BPacketAnyType.STRING)
            packet.writeString(value)
            
        elif (value_type == list):
            packet.writeUInt8(BPacketAnyType.ARRAY)
            packet.writeUInt8(len(value))
            for item in value:
                BPacketAny.write(packet, item)
                
        elif (value_type == dict):
            packet.writeUInt8(BPacketAnyType.TABLE)
            packet.writeUInt8(len(value))
            for key, item in value.items():
                packet.writeString(key)
                BPacketAny.write(packet, item)
                
    @staticmethod
    def read(packet):
        
        value_type = packet.readUInt8()
        
        if (value_type == BPacketAnyType.NULL):
            return None
        
        elif (value_type == BPacketAnyType.BOOL):
            return packet.readBool()
        
        elif (value_type == BPacketAnyType.INT8):
            return packet.readInt8()
        elif (value_type == BPacketAnyType.INT16):
            return packet.readInt16()
        elif (value_type == BPacketAnyType.INT32):
            return packet.readInt32()
        
        elif (value_type == BPacketAnyType.UINT8):
            return packet.readUInt8()
        elif (value_type == BPacketAnyType.UINT16):
            return packet.readUInt16()
        
        elif (value_type == BPacketAnyType.FLOAT):
            return packet.readFloat()
        
        elif (value_type == BPacketAnyType.STRING):
            return packet.readString()
        
        elif (value_type == BPacketAnyType.ARRAY):
            count = packet.readUInt8()
            tmp = list()
            
            for x in range(0, count):
                tmp.append(BPacketAny.read(packet))
                
            return tmp
                
        elif (value_type == BPacketAnyType.TABLE):
            count = packet.readUInt8()
            tmp = dict()
            
            for x in range(0, count):
                key = packet.readString()
                tmp[key] = BPacketAny.read(packet)
                
            return tmp

class BPacketArray:
    
    @staticmethod
    def write(packet, value):
        BPacketAny.write(packet, value)
        
    @staticmethod
    def read(packet):
        return BPacketAny.read(packet)
            
class BPacketTable:
    
    @staticmethod
    def write(packet, value):
        BPacketAny.write(packet, value)
        
    @staticmethod
    def read(packet):
        return BPacketAny.read(packet)