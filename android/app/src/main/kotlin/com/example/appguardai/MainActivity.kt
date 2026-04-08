package com.example.appguardai

import android.os.Environment
import android.os.StatFs
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.appguardai/storage"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "getTotalSpace" -> {
                    try {
                        val stat = StatFs(Environment.getDataDirectory().path)
                        val totalBytes = stat.blockSizeLong * stat.blockCountLong
                        result.success(totalBytes)
                    } catch (e: Exception) {
                        result.error("UNAVAILABLE", "Storage not available.", null)
                    }
                }
                "getFreeSpace" -> {
                    try {
                        val stat = StatFs(Environment.getDataDirectory().path)
                        val freeBytes = stat.blockSizeLong * stat.availableBlocksLong
                        result.success(freeBytes)
                    } catch (e: Exception) {
                        result.error("UNAVAILABLE", "Storage not available.", null)
                    }
                }
                else -> {
                    result.notImplemented()
                }
            }
        }
    }
}
