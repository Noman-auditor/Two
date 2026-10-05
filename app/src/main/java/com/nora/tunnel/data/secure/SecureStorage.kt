
package com.nora.tunnel.data.secure
import android.content.Context; import androidx.security.crypto.EncryptedSharedPreferences; import androidx.security.crypto.MasterKey
class SecureStorage(c: Context){ private val mk=MasterKey.Builder(c).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(); private val p=EncryptedSharedPreferences.create(c,"secure_creds",mk,EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV, EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
fun saveSecret(id:String,v:String)=p.edit().putString(id,v).apply(); fun getSecret(id:String)=p.getString(id,null) }
