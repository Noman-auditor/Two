
package com.nora.tunnel.notification; import android.app.Service; import android.content.Intent; import android.os.IBinder; class VpnForegroundService: Service(){ override fun onBind(i: Intent?): IBinder? = null }
