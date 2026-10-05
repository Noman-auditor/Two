
package com.nora.tunnel.tunnel; import com.nora.tunnel.core.model.TunnelProfile; import kotlinx.coroutines.flow.Flow
interface TunnelAdapter { suspend fun validate(p: TunnelProfile): Result<Unit>; suspend fun prepare(p: TunnelProfile): Result<Unit>; suspend fun connect(p: TunnelProfile, s: NoraVpnService): Result<ConnectionState>; suspend fun disconnect(); fun status(): Flow<ConnectionState>; fun statistics(): Flow<TrafficStats> }
enum class ConnectionState { IDLE, VALIDATING, PREPARING, CONNECTING, CONNECTED, RECONNECTING, DISCONNECTING, DISCONNECTED, ERROR }
data class TrafficStats(val rxBytes: Long, val txBytes: Long, val latencyMs: Long? = null, val uptimeSec: Long = 0)
