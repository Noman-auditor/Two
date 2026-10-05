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
""")

w("app/src/main/java/com/nora/tunnel/data/database/NoraDatabase.kt", """package com.nora.tunnel.data.database
import androidx.room.*
import com.nora.tunnel.core.model.TunnelProfile
import kotlinx.coroutines.flow.Flow
@Database(entities=[TunnelProfile::class], version=1, exportSchema=false)
@TypeConverters(Converters::class)
abstract class NoraDatabase: RoomDatabase(){ abstract fun dao(): ProfileDao }
@Dao interface ProfileDao{ @Query("SELECT * FROM profiles") fun observeAll(): Flow<List<TunnelProfile>>; @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun upsert(p: TunnelProfile); @Delete suspend fun delete(p: TunnelProfile) }
""")

w(".github/workflows/build.yml", """name: Build Nora Tunnel APK
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: \'temurin\', java-version: \'17\' }
      - uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: 8.7
      - name: Build APK
        run: gradle assembleDebug --stacktrace
      - uses: actions/upload-artifact@v4
        with: { name: Nora-Tunnel-APK, path: app/build/outputs/apk/debug/*.apk }
""")
