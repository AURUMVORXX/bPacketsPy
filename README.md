
# About

This is implementation of [bPackets](https://gitlab.com/bcore1/bpackets) module adapted for [PyG2O](https://github.com/AURUMVORXX/PyG2O)
## Comapring to original bPackets
1. Removed type BPacketObject due to the inabillity to transfer its scheme
2. BPacketArray and BPacketTable is now the same thing as BPacketAny (no need to specify them, unless you want to)

Python specific changes:
1. You don't need to specify BPacketAny type, it's default for any supported type of data, but specifying it lead to less packet size (except for BPacketArray and BPacketTable)

### NOTE:
It's important to use same names for class names derived from BPacketMessage and same names and amount of their properties. 
**bPacketsPy** generating unique integer ID based on class name, and also sorting all properties in alphabetic order before serialization and deserialization. So, if you'll use different class names - they'll not match and your packet will be lost, or if you'll use different properties names and amount of 'em, then there is high chances that your data will be corrupted.
## Installation
1. Download this repo
2. Import `meta.xml` from `bpackets_sq` to the client-side (and also to the server-side, if you want to)
3. Put `bpacket` folder into your `lib/` folder in the server root directory
4. Import `bpacket` into your Python scripts
## Usage example
### Python (server-side):
```python
import bpackets as bp
import g2o

class PlayerMessage(bp.BPacketMessage):
	name 	: bp.BPacketString 	= None
	pid 	: bp.BPacketUInt8 	= None
	
	# Type is not specified, BPacketAny will be used
	pclass 			        = None
	
	# Useless specification, BPacketAny will be used, but why not
	pattrs	: bp.BPacketTable 	= None

@g2o.event('onPlayerJoin')
def evtJoin(**kwargs):
	playerid = kwargs['playerid']
	msg = PlayerMessage(name = g2o.getPlayerName(pid), pid = playerid, pattrs = {'hp': 40, 'str': 500})
	msg.serialize().send(pid, RELIABLE)

class ClientMessage(bp.BPacketMessage):
	text = None

@ClientMessage.bind
def messageReader(pid, message):
	print(f'Client {pid} says {message.text}')
```

### Squirrel (client-side):
```cpp
class PlayerMessage extends BPacketMessage
{
	</ type = BPacketString />
	name = -1
	
	</ type = BPacketUInt8 />
	pid = -1

	</ type = BPacketAny />
	pclass = -1

	</ type = BPacketTable />
	pattrs = -1
}

class ClientMessage extends BPacketMessage
{
	</ type = BPacketAny />
	text = -1
}

PlayerMessage.bind(function(message){
	print("Got player info from server:");
	print("Player name: " + message.name);
	print("Player ID: " + message.pid);
	print("Player stats: ");
	foreach(key, value in message.pattrs)
		print(key + ": " + value);

	print("Sending response...");
	ClientMessage("Hello!").serialize().send(RELIABLE);
});
```
