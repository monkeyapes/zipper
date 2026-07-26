package com.localname.hider.ui;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.Settings;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import com.localname.hider.inject.AddonManager;
import com.localname.hider.inject.PackBuilder;
import com.localname.hider.inject.WorldInjector;
import com.localname.hider.service.WatchdogService;

import java.io.File;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_CODE = 100;
    private AddonManager addonManager;
    private TextView statusText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(getResources().getIdentifier("activity_main", "layout", getPackageName()));
        statusText = findViewById(getResources().getIdentifier("statusText", "id", getPackageName()));
        addonManager = new AddonManager(this);
        requestNeededPermissions();
    }

    private void requestNeededPermissions() {
        if (Build.VERSION.SDK_INT >= 30) {
            if (!Environment.isExternalStorageManager()) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                intent.setData(android.net.Uri.parse("package:" + getPackageName()));
                startActivityForResult(intent, REQUEST_CODE);
                return;
            }
        }
        if (Build.VERSION.SDK_INT >= 33) {
            if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQUEST_CODE);
                return;
            }
        }
        doInject();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE) doInject();
    }

    @Override
    public void onRequestPermissionsResult(int code, @NonNull String[] perms, @NonNull int[] results) {
        super.onRequestPermissionsResult(code, perms, results);
        doInject();
    }

    private void doInject() {
        statusText.setText("Installing addon...");
        new Thread(() -> {
            try {
                File bpDir = addonManager.getAddonBpDir();
                File rpDir = addonManager.getAddonRpDir();

                PackBuilder.extractAddonFromAssets(this);
                PackBuilder.rebuildPlayerEntity(bpDir, addonManager.getHideTag(), null);

                File[] worlds = WorldInjector.findWorlds();
                int count = 0;
                for (File w : worlds) {
                    if (WorldInjector.injectWorld(w, bpDir, rpDir)) count++;
                }

                final int done = count;
                final int total = worlds.length;
                runOnUiThread(() -> {
                    statusText.setText("Installed in " + done + "/" + total + " worlds");
                    Toast.makeText(this, "Addon installed in " + done + " worlds", Toast.LENGTH_LONG).show();
                });

                startWatchdog();
            } catch (Exception e) {
                runOnUiThread(() -> {
                    statusText.setText("Error: " + e.getMessage());
                });
            }
        }).start();
    }

    private void startWatchdog() {
        Intent intent = new Intent(this, WatchdogService.class);
        if (Build.VERSION.SDK_INT >= 26) {
            startForegroundService(intent);
        } else {
            startService(intent);
        }
    }
}
