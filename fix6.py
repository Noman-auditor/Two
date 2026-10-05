import os
def w(p,c):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    open(p,"w").write(c)
    print("fixed",p)

w("app/src/main/java/com/nora/tunnel/data/database/Converters.kt", """package com.nora.tunnel.data.database
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
""")

w("app/build.gradle.kts", """plugins {
    id("com.android.application") version "8.3.2"
    id("org.jetbrains.kotlin.android") version "1.9.22"
    id("org.jetbrains.kotlin.plugin.parcelize") version "1.9.22"
    id("org.jetbrains.kotlin.plugin.serialization") version "1.9.22"
    id("com.google.devtools.ksp") version "1.9.22-1.0.17"
}
android {
    namespace = "com.nora.tunnel"
    compileSdk = 34
    defaultConfig { applicationId = "com.nora.tunnel"; minSdk = 29; targetSdk = 34; versionCode = 1; versionName = "1.0.0" }
    compileOptions { sourceCompatibility = org.gradle.api.JavaVersion.VERSION_17; targetCompatibility = org.gradle.api.JavaVersion.VERSION_17 }
    buildFeatures { compose = true }
    composeOptions { kotlinCompilerExtensionVersion = "1.5.8" }
    kotlinOptions { jvmTarget = "17" }
    packaging { resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" } }
}
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
