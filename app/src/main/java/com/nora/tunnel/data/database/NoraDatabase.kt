
package com.nora.tunnel.data.database; import androidx.room.*; import com.nora.tunnel.core.model.TunnelProfile; import kotlinx.coroutines.flow.Flow
@Database(entities=[TunnelProfile::class], version=1, exportSchema=false) abstract class NoraDatabase: RoomDatabase(){ abstract fun dao(): ProfileDao }
@Dao interface ProfileDao{ @Query("SELECT * FROM profiles") fun observeAll(): Flow<List<TunnelProfile>>; @Insert(onConflict=OnConflictStrategy.REPLACE) suspend fun upsert(p: TunnelProfile); @Delete suspend fun delete(p: TunnelProfile) }
