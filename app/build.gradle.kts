plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("org.jetbrains.kotlin.plugin.parcelize") version "1.9.22"; id("org.jetbrains.kotlin.plugin.serialization") version "1.9.22"; id("com.google.devtools.ksp") version "1.9.22-1.0.17" }
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
