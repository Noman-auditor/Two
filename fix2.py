import os
def w(p,c):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    open(p,"w").write(c)
    print("created",p)

w("settings.gradle.kts", """pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "NoraTunnel"
include(":app")
""")

w("gradle.properties", """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRResources=true
""")

w("app/build.gradle.kts", """plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("org.jetbrains.kotlin.plugin.serialization") version "1.9.22"; id("com.google.devtools.ksp") version "1.9.22-1.0.17" }
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
""")

w("app/src/main/AndroidManifest.xml", """<manifest xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools">
    <uses-permission android:name="android.permission.INTERNET" /><uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" /><uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <application android:name=".NoraApp" android:theme="@android:style/Theme.NoTitleBar">
        <activity android:name=".MainActivity" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN" /><category android:name="android.intent.category.LAUNCHER" /></intent-filter></activity>
        <service android:name=".tunnel.NoraVpnService" android:permission="android.permission.BIND_VPN_SERVICE" android:exported="true"><intent-filter><action android:name="android.net.VpnService" /></intent-filter></service>
    </application>
</manifest>
""")

w("app/src/main/java/com/nora/tunnel/core/model/TunnelProfile.kt", """package com.nora.tunnel.core.model
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
""")
