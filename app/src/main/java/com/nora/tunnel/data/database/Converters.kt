package com.nora.tunnel.data.database
import androidx.room.TypeConverter
import com.nora.tunnel.core.model.Core
import com.nora.tunnel.core.model.Protocol
import com.nora.tunnel.core.model.Security
import com.nora.tunnel.core.model.Transport
object Converters {
    @TypeConverter @JvmStatic fun fromProtocol(v: Protocol) = v.name
    @TypeConverter @JvmStatic fun toProtocol(v: String) = Protocol.valueOf(v)
    @TypeConverter @JvmStatic fun fromCore(v: Core) = v.name
    @TypeConverter @JvmStatic fun toCore(v: String) = Core.valueOf(v)
    @TypeConverter @JvmStatic fun fromTransport(v: Transport) = v.name
    @TypeConverter @JvmStatic fun toTransport(v: String) = Transport.valueOf(v)
    @TypeConverter @JvmStatic fun fromSecurity(v: Security) = v.name
    @TypeConverter @JvmStatic fun toSecurity(v: String) = Security.valueOf(v)
}
