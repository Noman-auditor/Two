package com.nora.tunnel.data.database
import androidx.room.TypeConverter
import com.nora.tunnel.core.model.Core
import com.nora.tunnel.core.model.Protocol
import com.nora.tunnel.core.model.Security
import com.nora.tunnel.core.model.Transport
class Converters {
    @TypeConverter fun fromProtocol(v: Protocol) = v.name
    @TypeConverter fun toProtocol(v: String) = Protocol.valueOf(v)
    @TypeConverter fun fromCore(v: Core) = v.name
    @TypeConverter fun toCore(v: String) = Core.valueOf(v)
    @TypeConverter fun fromTransport(v: Transport) = v.name
    @TypeConverter fun toTransport(v: String) = Transport.valueOf(v)
    @TypeConverter fun fromSecurity(v: Security) = v.name
    @TypeConverter fun toSecurity(v: String) = Security.valueOf(v)
}
