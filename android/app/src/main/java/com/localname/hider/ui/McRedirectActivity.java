package com.localname.hider.ui;

import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class McRedirectActivity extends AppCompatActivity {
    private static final String[] LEVI_PACKAGES = {
        "com.levilab.levilauncher",
        "com.levilabs.levilauncher",
        "com.levilauncher",
        "com.levilab.levilauncher.partner",
        "com.levilauncher.app"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent incoming = getIntent();
        Uri data = incoming.getData();
        String type = incoming.getType();

        String targetPkg = findLeviLauncher();
        if (targetPkg != null) {
            Intent out = new Intent(Intent.ACTION_VIEW);
            out.setPackage(targetPkg);
            if (data != null) out.setData(data);
            if (type != null) out.setType(type);
            if (incoming.getExtras() != null)
                out.putExtras(incoming.getExtras());
            out.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            try {
                startActivity(out);
                finish();
                return;
            } catch (Exception ignored) { }
        }

        Toast.makeText(this, "LeviLauncher not found", Toast.LENGTH_LONG).show();
        finish();
    }

    private String findLeviLauncher() {
        PackageManager pm = getPackageManager();
        for (String pkg : LEVI_PACKAGES) {
            try {
                pm.getPackageInfo(pkg, 0);
                return pkg;
            } catch (Exception ignored) { }
        }
        return null;
    }
}
