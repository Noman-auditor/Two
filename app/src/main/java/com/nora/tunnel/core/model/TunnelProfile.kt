package com.nora.tunnel.core.model
import android.os.Parcelable
import androidx.room.Entity
import androidx.room.PrimaryKey
import kotlinx.parcelize.Parcelize
import java.util.UUID
enum class Protocol { VLESS, VMESS, TROJAN, SHADOWSOCKS, WIREGUARD, OPENVPN, SSH, HYSTERIA2, TUIC, SOCKS, HTTP }
enum class Core { XRAY, SINGBOX, WIREGUARD, OPENVPN, SSH, IKEV2 }
enum class Transport { TCP, UDP, TLS, WS, GRPC, QUIC, HTTP2 }
enum class Security { NONE, TLS, REALITY }
@Parcelize @Entity(tableName = "profiles")
data class TunnelProfile(@PrimaryKey val id: String = UUID.randomUUID().toString(), val name: String, val protocol: Protocol, val core: Core, val transport: Transport, val security: Security = Security.NONE, val serverAddress: String, val port: Int, val createdAt: Long = System.currentTimeMillis(), val updatedAt: Long = System.currentTimeMillis()) : Parcelable
