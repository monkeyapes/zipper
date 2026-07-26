package com.localname.hider.service;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import com.localname.hider.inject.AddonManager;
import com.localname.hider.inject.PackBuilder;
import com.localname.hider.inject.WorldInjector;

import java.io.File;

public class LiveUpdateReceiver extends BroadcastReceiver {
    private static final String TAG = "LiveUpdateReceiver";
    private static final String ACTION_LIVE_UPDATE = "com.localname.action.LIVE_UPDATE";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (!ACTION_LIVE_UPDATE.equals(intent.getAction())) return;

        String tmp = intent.getStringExtra("hide_tag");
        final String hideTag = tmp != null ? tmp : "\u00a70\u00a7k";

        String namesRaw = intent.getStringExtra("blocked_names");
        final String[] blockedNames;
        if (namesRaw != null && !namesRaw.isEmpty()) {
            blockedNames = namesRaw.split("\\|");
        } else {
            blockedNames = null;
        }

        Log.i(TAG, "Live update: hideTag=" + hideTag
            + " blockedNames=" + (blockedNames != null ? blockedNames.length : 0));

        new Thread(() -> {
            try {
                AddonManager mgr = new AddonManager(context);
                File bpDir = mgr.getAddonBpDir();
                File rpDir = mgr.getAddonRpDir();

                PackBuilder.extractAddonFromAssets(context);
                PackBuilder.rebuildPlayerEntity(bpDir, hideTag, blockedNames);

                File[] worlds = WorldInjector.findWorlds();
                int count = 0;
                for (File w : worlds) {
                    if (WorldInjector.injectWorld(w, bpDir, rpDir)) count++;
                }
                Log.i(TAG, "Live update: re-injected " + count + "/" + worlds.length + " worlds");
            } catch (Exception e) {
                Log.e(TAG, "Live update failed", e);
            }
        }).start();
    }
}
