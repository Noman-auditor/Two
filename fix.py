import os, textwrap
def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path,'w').write(textwrap.dedent(content))
    print("created", path)

w("app/src/main/java/com/nora/tunnel/tunnel/NoraVpnService.kt", """
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
            ACTION_CONNECT -> { val p=i.getParcelableExtra<TunnelProfile>("profile")!!; scope.launch{ try{ val b=Builder().addAddress("10.8.0.2",32).addRoute("0.0.0.0",0).addDnsServer("1.1.1.1").setSession(p.name).setMtu(1500); vpnInterface=b.establish()?:throw IllegalStateException("permission denied"); startForeground(1, NotificationHelper.createConnectedNotification(this@p, p)) }catch(e:Exception){Log.e("NoraVpn","Failed",e)} } }
            ACTION_DISCONNECT -> { try{vpnInterface?.close()}catch(_:Exception){}; stopSelf() }
        }
        return START_NOT_STICKY
    }
    override fun onDestroy(){ try{vpnInterface?.close()}catch(_:Exception){}; super.onDestroy() }
}
""")

w("app/src/main/java/com/nora/tunnel/data/secure/SecureStorage.kt", """
package com.nora.tunnel.data.secure
import android.content.Context; import androidx.security.crypto.EncryptedSharedPreferences; import androidx.security.crypto.MasterKey
class SecureStorage(c: Context){ private val mk=MasterKey.Builder(c).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(); private val p=EncryptedSharedPreferences.create(c,"secure_creds",mk,EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV, EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
fun saveSecret(id:String,v:String)=p.edit().putString(id,v).apply(); fun getSecret(id:String)=p.getString(id,null) }
""")

w("app/src/main/java/com/nora/tunnel/MainActivity.kt", """
package com.nora.tunnel
import android.content.Intent; import android.net.VpnService; import android.os.Bundle
import androidx.activity.ComponentActivity; import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.navigation.compose.rememberNavController
import com.nora.tunnel.core.model.TunnelProfile; import com.nora.tunnel.notification.NotificationHelper
import com.nora.tunnel.tunnel.NoraVpnService; import com.nora.tunnel.ui.navigation.NoraNavHost; import com.nora.tunnel.ui.theme.NoraTheme
class MainActivity : ComponentActivity() {
    private var pending: TunnelProfile? = null
    private val perm = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { if(it.resultCode==RESULT_OK) pending?.let{ startVpn(it)} }
    override fun onCreate(b: Bundle?) { super.onCreate(b); NotificationHelper.createChannel(this); setContent { NoraTheme { NoraNavHost(rememberNavController()) } } }
    fun requestConnect(p: TunnelProfile){ pending=p; val i=VpnService.prepare(this); if(i!=null) perm.launch(i) else startVpn(p) }
    private fun startVpn(p: TunnelProfile){ startService(Intent(this, NoraVpnService::class.java).apply{ action=NoraVpnService.ACTION_CONNECT; putExtra("profile", p)}) }
}
""")

w("app/src/main/java/com/nora/tunnel/ui/theme/Theme.kt", """
package com.nora.tunnel.ui.theme; import androidx.compose.material3.*; import androidx.compose.runtime.Composable; import androidx.compose.ui.graphics.Color
private val s=darkColorScheme(primary=Color(0xFF7C4DFF), background=Color(0xFF0A0E1A)); @Composable fun NoraTheme(c: @Composable ()->Unit){ MaterialTheme(colorScheme=s, content=c)}
""")

w("app/src/main/java/com/nora/tunnel/ui/navigation/NavGraph.kt", """
package com.nora.tunnel.ui.navigation; import androidx.compose.runtime.Composable; import androidx.navigation.NavHostController; import androidx.navigation.compose.NavHost; import androidx.navigation.compose.composable; import com.nora.tunnel.ui.screens.home.HomeScreen
@Composable fun NoraNavHost(n: NavHostController){ NavHost(n, startDestination="home"){ composable("home"){ HomeScreen() } } }
""")

w("app/src/main/java/com/nora/tunnel/ui/screens/home/HomeScreen.kt", """
package com.nora.tunnel.ui.screens.home; import androidx.compose.foundation.layout.*; import androidx.compose.material3.*; import androidx.compose.runtime.Composable; import androidx.compose.ui.Alignment; import androidx.compose.ui.Modifier; import androidx.compose.ui.unit.dp
@Composable fun HomeScreen(){ Column(Modifier.fillMaxSize().padding(16.dp), Arrangement.Center, Alignment.CenterHorizontally){ Text("NORA TUNNEL", style=MaterialTheme.typography.headlineMedium); Text("Secure. Private. Connected.", style=MaterialTheme.typography.labelSmall); Spacer(Modifier.height(24.dp)); Text("● DISCONNECTED"); Button(onClick={}){ Text("CONNECT") } } }
""")

w("app/src/main/java/com/nora/tunnel/notification/NotificationHelper.kt", """
package com.nora.tunnel.notification; import android.app.*; import android.content.Context; import android.content.Intent; import androidx.core.app.NotificationCompat; import com.nora.tunnel.core.model.TunnelProfile; import com.nora.tunnel.tunnel.NoraVpnService
object NotificationHelper{ const val CHANNEL_ID="nora_vpn"; fun createChannel(c: Context){ if(android.os.Build.VERSION.SDK_INT>=26){ val ch=NotificationChannel(CHANNEL_ID,"Nora Tunnel", NotificationManager.IMPORTANCE_LOW); (c.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(ch)}}
fun createConnectedNotification(c: Context, p: TunnelProfile): Notification = NotificationCompat.Builder(c, CHANNEL_ID).setSmallIcon(android.R.drawable.ic_menu_upload).setContentTitle("Nora Tunnel • "+p.name).setContentText("● CONNECTED").setOngoing(true).addAction(0,"DISCONNECT", PendingIntent.getService(c,0,Intent(c,NoraVpnService::class.java).setAction(NoraVpnService.ACTION_DISCONNECT), PendingIntent.FLAG_IMMUTABLE)).setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE).build() }
""")

w("app/src/main/java/com/nora/tunnel/notification/VpnForegroundService.kt", """
package com.nora.tunnel.notification; import android.app.Service; import android.content.Intent; import android.os.IBinder; class VpnForegroundService: Service(){ override fun onBind(i: Intent?): IBinder? = null }
""")

w("app/src/main/java/com/nora/tunnel/data/database/NoraDatabase.kt", """
package com.nora.tunnel.data.database; import androidx.room.*; import com.nora.tunnel.core.model.TunnelProfile; import kotlinx.coroutines.flow.Flow
@Database(entities=[TunnelProfile::class], version=1, exportSchema=false) abstract class NoraDatabase: RoomDatabase(){ abstract fun dao(): ProfileDao }
@Dao interface ProfileDao{ @Query("SELECT * FROM profiles") fun observeAll(): Flow<List<TunnelProfile>>; @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun upsert(p: TunnelProfile); @Delete suspend fun delete(p: TunnelProfile) }
""")

w("app/src/main/java/com/nora/tunnel/core/CapabilityRegistry.kt", """
package com.nora.tunnel.core; import com.nora.tunnel.core.model.*
object CapabilityRegistry {
    data class Capability(val core: Core, val protocols: Set<Protocol>, val transports: Set<Transport>)
    val registry = listOf(
        Capability(Core.XRAY, setOf(Protocol.VLESS, Protocol.VMESS, Protocol.TROJAN, Protocol.SHADOWSOCKS), setOf(Transport.TCP, Transport.WS, Transport.GRPC, Transport.QUIC, Transport.TLS)),
        Capability(Core.SINGBOX, setOf(Protocol.VLESS, Protocol.HYSTERIA2, Protocol.TUIC, Protocol.SHADOWSOCKS), setOf(Transport.TCP, Transport.UDP, Transport.WS, Transport.QUIC)),
        Capability(Core.WIREGUARD, setOf(Protocol.WIREGUARD), setOf(Transport.UDP)),
        Capability(Core.OPENVPN, setOf(Protocol.OPENVPN), setOf(Transport.TCP, Transport.UDP)),
        Capability(Core.SSH, setOf(Protocol.SSH), setOf(Transport.TCP, Transport.WS, Transport.TLS))
    )
    fun isValid(p: Protocol, c: Core, t: Transport) = registry.find { it.core == c && p in it.protocols }?.transports?.contains(t) == true
}
""")

w("app/src/main/java/com/nora/tunnel/tunnel/TunnelAdapter.kt", """
package com.nora.tunnel.tunnel; import com.nora.tunnel.core.model.TunnelProfile; import kotlinx.coroutines.flow.Flow
interface TunnelAdapter { suspend fun validate(p: TunnelProfile): Result<Unit>; suspend fun prepare(p: TunnelProfile): Result<Unit>; suspend fun connect(p: TunnelProfile, s: NoraVpnService): Result<ConnectionState>; suspend fun disconnect(); fun status(): Flow<ConnectionState>; fun statistics(): Flow<TrafficStats> }
enum class ConnectionState { IDLE, VALIDATING, PREPARING, CONNECTING, CONNECTED, RECONNECTING, DISCONNECTING, DISCONNECTED, ERROR }
data class TrafficStats(val rxBytes: Long, val txBytes: Long, val latencyMs: Long? = null, val uptimeSec: Long = 0)
""")

w(".github/workflows/build.yml", """
name: Build Nora Tunnel APK
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Build APK
        run: gradle assembleDebug --stacktrace
      - uses: actions/upload-artifact@v4
        with: { name: Nora-Tunnel-APK, path: app/build/outputs/apk/debug/*.apk }
""")
print("ALL DONE")
