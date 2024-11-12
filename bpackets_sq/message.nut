
///////////////////////////////////////////
/// Registry
///////////////////////////////////////////
local registered = []

//-----------------------------------------

local function generateId(className)
{
    local id = 1
    foreach(x in className)
       id = ((x << 16) | x.tochar().toupper()[0] >> 16) ^ id

    return id
}

class BPacketMessage {
    __id = null
    __meta = null
    __fields = null
    __handlers = null

    constructor(...) {
        local len = vargv.len()
        for (local i = 0; i < len; ++i) {
            local attrs = this.__fields[i]
            this[attrs.field] = vargv[i]
        }

        local className = null
        foreach(k, v in getroottable())
            if (v == this.getclass())
                className = k;

        if (this.__id.len() == 0)
            this.__id.push(generateId(className))
    }

    function header() {
        return this.__id[0]
    }

    function write(packet, message = null) {
        local message = message || this

        local sortFields = clone this.__fields;
        sortFields.sort(@(a,b) a.field <=> b.field)

        foreach (attrs in sortFields)
            attrs.type.write(packet, message[attrs.field])
    }

    function read(packet) {
        local message = this()

        local sortFields = clone this.__fields;
        sortFields.sort(@(a,b) a.field <=> b.field)

        foreach (attrs in sortFields)
            message[attrs.field] = attrs.type.read(packet)

        return message
    }

    function serialize() {
        local packet = Packet()
        packet.writeUInt32(this.header())

        this.write(packet)
        return packet
    }

    static function deserialize(packet, skip_header = false) {
        if (!skip_header) {
            packet.readUInt32() // Just change offset
        }

        return this.read(packet)
    }

    static function bind(callback) {

        local className = null
        foreach(k, v in getroottable())
            if (v == this)
                className = k;

        if (this.__id.len() == 0)
            this.__id.push(generateId(className))

        this.__handlers.push(callback)
        return callback
    }

    static function unbind(callback) {
        local len = this.__handlers.len()
        for (local i = 0; i < len; ++i) {
            if (callback == this.__handlers[i]) {
                this.__handlers[i] = null
            }
        }

        this.__meta.dirty = true
    }

    static function clear() {
        this.__handlers.clear()
    }

    static function _cleanHandlers() {
        local len = this.__handlers.len()
        for (local i = 0; i < len;) {
            if (this.__handlers[i] == null) {
                this.__handlers[i] = this.__handlers[--len]
                this.__handlers.pop()
            } else {
                ++i
            }
        }

        this.__meta.dirty = false
    }

    ///////////////////////////////////////////
    /// Meta-methods
    ///////////////////////////////////////////

    function _inherited(attrs) {
        this.__fields <- []

        local is_abstract = attrs != null && "abstract" in attrs && attrs.abstract
        if (!is_abstract) {
            this.__handlers <- []
            this.__id <- []
            this.__meta <- {dirty = false}

            registered.push(this)
        }
	}

    function _newmember(index, value, attributes, is_static) {
        if (!is_static && attributes) {
            attributes.field <- index

            if (!("type" in attributes)) {
                throw "Missing 'type' in attributes for field '" + index + "'!"
            }

            this.__fields.push(attributes)
        }

        // Setup new members
        this[index] <- value
    }
}

///////////////////////////////////////////
/// Events
///////////////////////////////////////////

local function packet_handler(packet) {
    local header = packet.readUInt32()
    foreach(v in registered)
        if (v.header() == header)
            return v.deserialize(packet, true)

    return null
}

local function cli_packet_handler(packet) {
    local message = packet_handler(packet)
    if (message) {
        if (message.__meta.dirty) {
            message._cleanHandlers()
        }

        foreach (handler in message.__handlers) {
            handler(message)
        }
    }
}

local function srv_packet_handler(pid, packet) {
    local message = packet_handler(packet)
    if (message) {
        if (message.__meta.dirty) {
            message._cleanHandlers()
        }

        foreach (handler in message.__handlers) {
            handler(pid, message)
        }
    }
}

addEventHandler("onPacket", SERVER_SIDE ? srv_packet_handler : cli_packet_handler)
