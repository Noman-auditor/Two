package com.nora.tunnel.tunnel
import android.content.Intent; import android.net.VpnService; import android.os.ParcelFileDescriptor; import android.util.Log
import com.nora.tunnel.core.model.TunnelProfile; import com.nora.tunnel.notification.NotificationHelper; import kotlinx.coroutines.*
class NoraVpnService : VpnService() {
    companion object { const val ACTION_CONNECT = "CONNECT"; const val ACTION_DISCONNECT = "DISCONNECT"; var instance: NoraVpnService? = null }
    private var vpnInterface: ParcelFileDescriptor? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    override fun onCreate() { super.onCreate(); instance = this }
    override fun onStartCommand(i: Intent?, f: Int, s: Int): Int {
        when(i?.action) {
            ACTION_CONNECT -> { val p=i.getParcelableExtra<TunnelProfile>("profile")!!; scope.launch{ try{ val b=Builder().addAddress("10.8.0.2",32).addRoute("0.0.0.0",0).addDnsServer("1.1.1.1").setSession(p.name).setMtu(1500); vpnInterface=b.establish()?:throw IllegalStateException("permission denied"); startForeground(1, NotificationHelper.createConnectedNotification(this@NoraVpnService, p)) }catch(e:Exception){Log.e("NoraVpn","Failed",e)} } }
            ACTION_DISCONNECT -> { try{vpnInterface?.close()}catch(_:Exception){}; stopSelf() }
        }
        return START_NOT_STICKY
    }
    override fun onDestroy(){ try{vpnInterface?.close()}catch(_:Exception){}; super.onDestroy() }
}
