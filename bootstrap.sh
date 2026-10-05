#!/bin/bash
set -e
PROJECT=$(pwd)
echo "Creating NORA TUNNEL... $PROJECT"
mkdir -p app/src/main/java/com/nora/tunnel/{core/model,core,data/{database,datastore,repository,secure,log},domain/usecase,tunnel/{wireguard,xray},routing,lab,diagnostics,notification,ui/{theme,navigation,components,screens/{home,profiles,routing,lab,statistics,logs,security,settings}}}
mkdir -p app/src/main .github/workflows gradle/wrapper
cat > settings.gradle.kts <<\'EOF\'
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "NoraTunnel"
include(":app")
EOF
cat > gradle.properties <<\'EOF\'
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRResources=true
EOF
cat > app/build.gradle.kts <<\'EOF\'
plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("org.jetbrains.kotlin.plugin.serialization") version "1.9.22"; id("com.google.devtools.ksp") version "1.9.22-1.0.17" }
android { namespace = "com.nora.tunnel"; compileSdk = 34; defaultConfig { applicationId = "com.nora.tunnel"; minSdk = 29; targetSdk = 34; versionCode = 1; versionName = "1.0.0" }; buildFeatures { compose = true }; composeOptions { kotlinCompilerExtensionVersion = "1.5.8" }; kotlinOptions { jvmTarget = "17" }; packaging { resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" } } }
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui"); implementation("androidx.compose.material3:material3")
    implementation("androidx.navigation:navigation-compose:2.7.7")
    implementation("androidx.room:room-runtime:2.6.1"); implementation("androidx.room:room-ktx:2.6.1"); ksp("androidx.room:room-compiler:2.6.1")
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
EOF
cat > app/src/main/AndroidManifest.xml <<\'EOF\'
<manifest xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools">
    <uses-permission android:name="android.permission.INTERNET" /><uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" /><uses-permission android:name="android.permission.FOREGROUND_SERVICE" /><uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <application android:name=".NoraApp" android:theme="@android:style/Theme.NoTitleBar">
        <activity android:name=".MainActivity" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN" /><category android:name="android.intent.category.LAUNCHER" /></intent-filter></activity>
        <service android:name=".tunnel.NoraVpnService" android:permission="android.permission.BIND_VPN_SERVICE" android:exported="true"><intent-filter><action android:name="android.net.VpnService" /></intent-filter><property android:name="android.net.VpnService.SUPPORTS_ALWAYS_ON" android:value="true" /></service>
        <service android:name=".notification.VpnForegroundService" android:foregroundServiceType="specialUse"><property android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE" android:value="vpnTunnel"/></service>
    </application>
</manifest>
EOF
cat > app/src/main/java/com/nora/tunnel/core/model/TunnelProfile.kt <<\'EOF\'
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
EOF
cat > app/src/main/java/com/nora/tunnel/core/CapabilityRegistry.kt <<\'EOF\'
package com.nora.tunnel.core
import com.nora.tunnel.core.model.*
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
EOF
cat > app/src/main/java/com/nora/tunnel/tunnel/TunnelAdapter.kt <<\'EOF\'
package com.nora.tunnel.tunnel
import com.nora.tunnel.core.model.TunnelProfile
import kotlinx.coroutines.flow.Flow
interface TunnelAdapter {
    suspend fun validate(profile: TunnelProfile): Result<Unit>
    suspend fun prepare(profile: TunnelProfile): Result<Unit>
    suspend fun connect(profile: TunnelProfile, vpnService: NoraVpnService): Result<ConnectionState>
    suspend fun disconnect()
    fun status(): Flow<ConnectionState>
    fun statistics(): Flow<TrafficStats>
}
enum class ConnectionState { IDLE, VALIDATING, PREPARING, CONNECTING, CONNECTED, RECONNECTING, DISCONNECTING, DISCONNECTED, ERROR }
data class TrafficStats(val rxBytes: Long, val txBytes: Long, val latencyMs: Long? = null, val uptimeSec: Long = 0)
data class DiagnosticsResult(val name: String, val success: Boolean, val message: String?)
EOF
cat > app/src/main/java/com/nora/tunnel/tunnel/NoraVpnService.kt <<\'EOF\'
package com.nora.tunnel.tunnel
import android.content.Intent
import android.net.VpnService
import android.os.ParcelFileDescriptor
import android.util.Log
import com.nora.tunnel.core.model.TunnelProfile
import com.nora.tunnel.notification.NotificationHelper
import kotlinx.coroutines.*
class NoraVpnService : VpnService() {
    companion object { const val ACTION_CONNECT = "CONNECT"; const val ACTION_DISCONNECT = "DISCONNECT"; var instance: NoraVpnService? = null }
    private var vpnInterface: ParcelFileDescriptor? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    override fun onCreate() { super.onCreate(); instance = this }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when(intent?.action) {
            ACTION_CONNECT -> { val p = intent.getParcelableExtra<TunnelProfile>("profile")!!; scope.launch { establishVpn(p) } }
            ACTION_DISCONNECT -> { teardown(); stopSelf() }
        }
        return START_NOT_STICKY
    }
    private suspend fun establishVpn(profile: TunnelProfile) {
        if(profile.serverAddress.isBlank() || profile.port !in 1..65535) return
        try {
            val builder = Builder().addAddress("10.8.0.2", 32).addRoute("0.0.0.0", 0).addDnsServer("1.1.1.1").setSession(profile.name).setMtu(1500)
            vpnInterface = builder.establish() ?: throw IllegalStateException("VpnService not prepared")
            startForeground(1, NotificationHelper.createConnectedNotification(this, profile))
        } catch(e: Exception) { Log.e("NoraVpn", "Failed", e); teardown() }
    }
    private fun teardown() { try { vpnInterface?.close() } catch(_:Exception){}; vpnInterface=null; stopForeground(STOP_FOREGROUND_REMOVE) }
    override fun onRevoke() { teardown(); super.onRevoke() }
    override fun onDestroy() { teardown(); instance=null; super.onDestroy() }
}
EOF
mkdir -p app/src/main/java/com/nora/tunnel/data/secure
cat > app/src/main/java/com/nora/tunnel/data/secure/SecureStorage.kt <<\'EOF\'
package com.nora.tunnel.data.secure
import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
class SecureStorage(c: Context) {
    private val mk = MasterKey.Builder(c).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
    private val p = EncryptedSharedPreferences.create(c,"secure_creds",mk,EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV, EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
    fun saveSecret(id: String, v: String) = p.edit().putString(id,v).apply()
    fun getSecret(id: String) = p.getString(id,null)
    fun deleteSecret(id: String) = p.edit().remove(id).apply()
    fun redact(log: String) = log.replace(Regex("(password|privateKey|token)=[^\\s]+"), "$1=******")
}
EOF
cat > app/src/main/java/com/nora/tunnel/NoraApp.kt <<\'EOF\'
package com.nora.tunnel; import android.app.Application; class NoraApp: Application()
EOF
cat > app/src/main/java/com/nora/tunnel/MainActivity.kt <<\'EOF\'
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
EOF
for f in ui/theme/Theme ui/navigation/NavGraph ui/screens/home/HomeScreen notification/NotificationHelper notification/VpnForegroundService data/database/NoraDatabase; do mkdir -p $(dirname app/src/main/java/com/nora/tunnel/$f); done
cat > app/src/main/java/com/nora/tunnel/ui/theme/Theme.kt <<\'EOF\'
package com.nora.tunnel.ui.theme; import androidx.compose.material3.*; import androidx.compose.runtime.Composable; import androidx.compose.ui.graphics.Color
private val s=darkColorScheme(primary=Color(0xFF7C4DFF), background=Color(0xFF0A0E1A)); @Composable fun NoraTheme(c: @Composable ()->Unit){ MaterialTheme(colorScheme=s, content=c)}
EOF
cat > app/src/main/java/com/nora/tunnel/ui/navigation/NavGraph.kt <<\'EOF\'
package com.nora.tunnel.ui.navigation; import androidx.compose.runtime.Composable; import androidx.navigation.NavHostController; import androidx.navigation.compose.NavHost; import androidx.navigation.compose.composable; import com.nora.tunnel.ui.screens.home.HomeScreen
@Composable fun NoraNavHost(n: NavHostController){ NavHost(n, startDestination="home"){ composable("home"){ HomeScreen() } } }
EOF
cat > app/src/main/java/com/nora/tunnel/ui/screens/home/HomeScreen.kt <<\'EOF\'
package com.nora.tunnel.ui.screens.home; import androidx.compose.foundation.layout.*; import androidx.compose.material3.*; import androidx.compose.runtime.Composable; import androidx.compose.ui.Alignment; import androidx.compose.ui.Modifier; import androidx.compose.ui.unit.dp
@Composable fun HomeScreen(){ Column(Modifier.fillMaxSize().padding(16.dp), Arrangement.Center, Alignment.CenterHorizontally){ Text("NORA TUNNEL", style=MaterialTheme.typography.headlineMedium); Text("Secure. Private. Connected.", style=MaterialTheme.typography.labelSmall); Spacer(Modifier.height(24.dp)); Text("● DISCONNECTED"); Button(onClick={}){ Text("CONNECT") } } }
EOF
cat > app/src/main/java/com/nora/tunnel/notification/NotificationHelper.kt <<\'EOF\'
package com.nora.tunnel.notification; import android.app.*; import android.content.Context; import android.content.Intent; import androidx.core.app.NotificationCompat; import com.nora.tunnel.core.model.TunnelProfile; import com.nora.tunnel.tunnel.NoraVpnService
object NotificationHelper{ const val CHANNEL_ID="nora_vpn"; fun createChannel(c: Context){ if(android.os.Build.VERSION.SDK_INT>=26){ val ch=NotificationChannel(CHANNEL_ID,"Nora Tunnel", NotificationManager.IMPORTANCE_LOW); (c.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(ch)}}
fun createConnectedNotification(c: Context, p: TunnelProfile): Notification = NotificationCompat.Builder(c, CHANNEL_ID).setSmallIcon(android.R.drawable.ic_menu_upload).setContentTitle("Nora Tunnel • ${p.name}").setContentText("● CONNECTED").setOngoing(true).addAction(0,"DISCONNECT", PendingIntent.getService(c,0,Intent(c,NoraVpnService::class.java).setAction(NoraVpnService.ACTION_DISCONNECT), PendingIntent.FLAG_IMMUTABLE)).setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE).build() }
EOF
cat > app/src/main/java/com/nora/tunnel/notification/VpnForegroundService.kt <<\'EOF\'
package com.nora.tunnel.notification; import android.app.Service; import android.content.Intent; import android.os.IBinder; class VpnForegroundService: Service(){ override fun onBind(i: Intent?): IBinder? = null }
EOF
cat > app/src/main/java/com/nora/tunnel/data/database/NoraDatabase.kt <<\'EOF\'
package com.nora.tunnel.data.database; import androidx.room.*; import com.nora.tunnel.core.model.TunnelProfile; import kotlinx.coroutines.flow.Flow
@Database(entities=[TunnelProfile::class], version=1, exportSchema=false) abstract class NoraDatabase: RoomDatabase(){ abstract fun dao(): ProfileDao }
@Dao interface ProfileDao{ @Query("SELECT * FROM profiles") fun observeAll(): Flow<List<TunnelProfile>>; @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun upsert(p: TunnelProfile); @Delete suspend fun delete(p: TunnelProfile) }
EOF
mkdir -p .github/workflows
cat > .github/workflows/build.yml <<\'EOF\'
name: Build Nora Tunnel APK
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: \'temurin\', java-version: \'17\' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Build APK
        run: gradle assembleDebug --stacktrace
      - uses: actions/upload-artifact@v4
        with: { name: Nora-Tunnel-APK, path: app/build/outputs/apk/debug/*.apk }
EOF
echo "✅ NORA TUNNEL All Fix Done"
