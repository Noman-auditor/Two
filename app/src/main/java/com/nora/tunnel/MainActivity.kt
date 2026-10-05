
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
