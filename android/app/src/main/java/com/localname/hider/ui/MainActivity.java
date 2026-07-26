package com.localname.hider.ui;

import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.Settings;
import android.widget.Button;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.localname.hider.inject.AddonManager;
import com.localname.hider.inject.PackBuilder;
import com.localname.hider.inject.WorldInjector;
import com.localname.hider.service.WatchdogService;
import com.localname.hider.util.Constants;
import com.localname.hider.util.PermissionHelper;
import com.localname.hider.zip.ZipViewerActivity;

import java.io.File;

public class MainActivity extends AppCompatActivity {
    private AddonManager addonManager;
    private Switch enableSwitch;
    private TextView worldCountText;
    private TextView statusText;
    private Button injectAllBtn;
    private Button removeAllBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(getResources().getIdentifier("activity_main",
            "layout", getPackageName()));

        addonManager = new AddonManager(this);

        enableSwitch = findViewById(getResources().getIdentifier("enableSwitch",
            "id", getPackageName()));
        worldCountText = findViewById(getResources().getIdentifier("worldCount",
            "id", getPackageName()));
        statusText = findViewById(getResources().getIdentifier("statusText",
            "id", getPackageName()));
        injectAllBtn = findViewById(getResources().getIdentifier("injectAllBtn",
            "id", getPackageName()));
        removeAllBtn = findViewById(getResources().getIdentifier("removeAllBtn",
            "id", getPackageName()));

        enableSwitch.setChecked(addonManager.isEnabled());
        requestPermissions();

        enableSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            addonManager.setEnabled(isChecked);
            if (isChecked) {
                startWatchdogService();
            }
            refreshStatus();
        });

        injectAllBtn.setOnClickListener(v -> injectAll());
        removeAllBtn.setOnClickListener(v -> removeAll());

        findViewById(getResources().getIdentifier("jarFixerBtn",
            "id", getPackageName()))
            .setOnClickListener(v -> startActivity(
                new Intent(MainActivity.this, JarFixerActivity.class)));

        findViewById(getResources().getIdentifier("zipBtn",
            "id", getPackageName()))
            .setOnClickListener(v -> openZipPicker());

        refreshStatus();
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshStatus();
    }

    private void requestPermissions() {
        if (!PermissionHelper.hasStoragePermission(this)) {
            PermissionHelper.requestStoragePermission(this);
        }
        if (Build.VERSION.SDK_INT >= 30) {
            if (!Environment.isExternalStorageManager()) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                intent.setData(Uri.parse("package:" + getPackageName()));
                startActivity(intent);
            }
        }
        if (!PermissionHelper.hasNotificationPermission(this)) {
            PermissionHelper.requestNotificationPermission(this);
        }
    }

    private void startWatchdogService() {
        Intent intent = new Intent(this, WatchdogService.class);
        if (Build.VERSION.SDK_INT >= 26) {
            startForegroundService(intent);
        } else {
            startService(intent);
        }
    }

    private void refreshStatus() {
        new Thread(() -> {
            File[] worlds = WorldInjector.findWorlds();
            int protectedCount = 0;
            for (File w : worlds) {
                if (WorldInjector.isPackInstalled(w)) protectedCount++;
            }
            final int total = worlds.length;
            final int prot = protectedCount;
            runOnUiThread(() -> {
                worldCountText.setText(total + " worlds found (" + prot + " protected)");
                statusText.setText(addonManager.isEnabled() ? "Protection Active" : "Protection Disabled");
                injectAllBtn.setEnabled(total > 0);
                removeAllBtn.setEnabled(total > 0);
            });
        }).start();
    }

    private void injectAll() {
        injectAllBtn.setEnabled(false);
        removeAllBtn.setEnabled(false);
        statusText.setText("Injecting...");
        new Thread(() -> {
            File bpDir = addonManager.getAddonBpDir();
            File rpDir = addonManager.getAddonRpDir();
            if (!new File(bpDir, "entities/player.json").exists()) {
                PackBuilder.extractAddonFromAssets(this);
            }
            File[] worlds = WorldInjector.findWorlds();
            int count = 0;
            for (File w : worlds) {
                if (WorldInjector.injectWorld(w, bpDir, rpDir)) count++;
            }
            final int done = count;
            runOnUiThread(() -> {
                statusText.setText("Injected into " + done + "/" + worlds.length + " worlds");
                refreshStatus();
                injectAllBtn.setEnabled(true);
                removeAllBtn.setEnabled(true);
                Toast.makeText(MainActivity.this,
                    "Done! " + done + " worlds", Toast.LENGTH_SHORT).show();
            });
        }).start();
    }

    private void removeAll() {
        injectAllBtn.setEnabled(false);
        removeAllBtn.setEnabled(false);
        statusText.setText("Removing...");
        new Thread(() -> {
            File[] worlds = WorldInjector.findWorlds();
            int count = 0;
            for (File w : worlds) {
                if (WorldInjector.removeFromWorld(w)) count++;
            }
            final int done = count;
            runOnUiThread(() -> {
                statusText.setText("Removed from " + done + " worlds");
                refreshStatus();
                injectAllBtn.setEnabled(true);
                removeAllBtn.setEnabled(true);
            });
        }).start();
    }

    private void openZipPicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        String[] mimeTypes = {"application/zip", "application/x-zip-compressed", "*/*"};
        intent.putExtra(Intent.EXTRA_MIME_TYPES, mimeTypes);
        startActivityForResult(intent, 9001);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 9001 && resultCode == RESULT_OK && data != null) {
            Uri uri = data.getData();
            Intent intent = new Intent(this, ZipViewerActivity.class);
            intent.putExtra("zip_uri", uri.toString());
            startActivity(intent);
        }
    }
}
