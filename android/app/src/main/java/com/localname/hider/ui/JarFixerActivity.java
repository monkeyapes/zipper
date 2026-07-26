package com.localname.hider.ui;

import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

public class JarFixerActivity extends AppCompatActivity {
    private TextView infoText;
    private Button selectApkBtn;
    private Button fixBtn;
    private String selectedApkPath;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(getResources().getIdentifier("activity_jar_fixer",
            "layout", getPackageName()));

        infoText = findViewById(getResources().getIdentifier("apkInfo",
            "id", getPackageName()));
        selectApkBtn = findViewById(getResources().getIdentifier("selectApkBtn",
            "id", getPackageName()));
        fixBtn = findViewById(getResources().getIdentifier("fixApkBtn",
            "id", getPackageName()));

        selectApkBtn.setOnClickListener(v -> pickApk());
        fixBtn.setOnClickListener(v -> fixApk());
        fixBtn.setEnabled(false);
    }

    private void pickApk() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/vnd.android.package-archive");
        startActivityForResult(intent, 1001);
    }

    private void fixApk() {
        if (selectedApkPath == null || !new File(selectedApkPath).exists()) {
            Toast.makeText(this, "Select a valid APK first", Toast.LENGTH_SHORT).show();
            return;
        }
        fixBtn.setEnabled(false);
        infoText.setText("Analyzing APK...");
        new Thread(() -> {
            try {
                ZipFile zf = new ZipFile(selectedApkPath);
                boolean hasManifest = false;
                int dexCount = 0, entryCount = 0;
                java.util.Enumeration<? extends ZipEntry> entries = zf.entries();
                while (entries.hasMoreElements()) {
                    ZipEntry e = entries.nextElement();
                    if (e.getName().equals("AndroidManifest.xml")) hasManifest = true;
                    if (e.getName().endsWith(".dex")) dexCount++;
                    entryCount++;
                }
                zf.close();
                final boolean valid = hasManifest && dexCount > 0;
                final int dCount = dexCount;
                final int eCount = entryCount;
                runOnUiThread(() -> {
                    infoText.setText("Entries: " + eCount + "\nDEX files: " + dCount
                        + "\nAndroidManifest: " + (hasManifest ? "Yes" : "No")
                        + "\nValid APK: " + (valid ? "Yes" : "No (may be corrupt)"));
                    if (valid) {
                        injectAddonIntoApk();
                    } else {
                        fixBtn.setEnabled(true);
                    }
                });
            } catch (Exception ex) {
                runOnUiThread(() -> {
                    infoText.setText("Error: " + ex.getMessage());
                    fixBtn.setEnabled(true);
                });
            }
        }).start();
    }

    private void injectAddonIntoApk() {
        infoText.setText("Injecting addon into APK...");
        new Thread(() -> {
            try {
                String outputPath = selectedApkPath.replace(".apk", "_patched.apk");
                java.io.FileInputStream fis = new java.io.FileInputStream(selectedApkPath);
                java.io.FileOutputStream fos = new java.io.FileOutputStream(outputPath);
                java.util.zip.ZipOutputStream zos = new java.util.zip.ZipOutputStream(fos);
                java.util.zip.ZipFile zf = new java.util.zip.ZipFile(selectedApkPath);

                for (java.util.Enumeration<? extends java.util.zip.ZipEntry> e = zf.entries(); e.hasMoreElements();) {
                    java.util.zip.ZipEntry entry = e.nextElement();
                    zos.putNextEntry(new java.util.zip.ZipEntry(entry.getName()));
                    java.io.InputStream is = zf.getInputStream(entry);
                    byte[] buf = new byte[4096];
                    int len;
                    while ((len = is.read(buf)) > 0) zos.write(buf, 0, len);
                    zos.closeEntry();
                    is.close();
                }
                zf.close();

                String[] addonFiles = {
                    "assets/addon/LocalName_BP/manifest.json",
                    "assets/addon/LocalName_BP/entities/player.json",
                    "assets/addon/LocalName_RP/manifest.json",
                    "assets/addon/LocalName_RP/entity/player.entity.json",
                };
                for (String path : addonFiles) {
                    zos.putNextEntry(new java.util.zip.ZipEntry(path));
                    java.io.InputStream is = getAssets().open(path);
                    byte[] buf = new byte[4096];
                    int len;
                    while ((len = is.read(buf)) > 0) zos.write(buf, 0, len);
                    zos.closeEntry();
                    is.close();
                }
                zos.close();
                fis.close();

                runOnUiThread(() -> {
                    infoText.setText("APK patched: " + outputPath);
                    fixBtn.setEnabled(true);
                    Toast.makeText(JarFixerActivity.this,
                        "APK saved to: " + outputPath, Toast.LENGTH_LONG).show();
                });
            } catch (Exception ex) {
                runOnUiThread(() -> {
                    infoText.setText("Error: " + ex.getMessage());
                    fixBtn.setEnabled(true);
                });
            }
        }).start();
    }

    private String getPathFromUri(Uri uri) {
        String path = uri.getPath();
        if (path != null && path.startsWith("/root/")) {
            path = path.replace("/root/", "/");
        }
        if (path != null && path.startsWith("/document/")) {
            path = path.replace("/document/", "/");
        }
        return path;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 1001 && resultCode == RESULT_OK && data != null) {
            Uri uri = data.getData();
            selectedApkPath = uri.getPath();
            // Try to copy to internal storage for processing
            try {
                File cacheFile = new File(getCacheDir(), "input.apk");
                InputStream is = getContentResolver().openInputStream(uri);
                FileOutputStream os = new FileOutputStream(cacheFile);
                byte[] buf = new byte[4096];
                int len;
                while ((len = is.read(buf)) > 0) os.write(buf, 0, len);
                is.close();
                os.close();
                selectedApkPath = cacheFile.getAbsolutePath();
                infoText.setText("APK loaded: " + cacheFile.length() + " bytes");
                fixBtn.setEnabled(true);
            } catch (Exception e) {
                infoText.setText("Error loading APK: " + e.getMessage());
            }
        }
    }
}
