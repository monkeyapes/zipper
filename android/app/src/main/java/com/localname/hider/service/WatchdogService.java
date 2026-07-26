package com.localname.hider.service;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;

import androidx.core.app.NotificationCompat;

import com.localname.hider.inject.AddonManager;
import com.localname.hider.inject.PackBuilder;
import com.localname.hider.inject.WorldInjector;
import com.localname.hider.util.Constants;

import java.io.File;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class WatchdogService extends Service {
    private static final String TAG = "WatchdogService";
    private static final int NOTIF_ID = 1001;
    private static final String CHANNEL_ID = "localname_watchdog";

    private ScheduledExecutorService scheduler;
    private AddonManager addonManager;

    @Override
    public void onCreate() {
        super.onCreate();
        addonManager = new AddonManager(this);
        createNotificationChannel();
        startForeground(NOTIF_ID, buildNotification());
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && Constants.INTENT_CHECK.equals(intent.getAction())) {
            runCheck();
            return START_NOT_STICKY;
        }

        scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleAtFixedRate(
            this::runCheck,
            0,
            Constants.WATCHDOG_INTERVAL_MS,
            TimeUnit.MILLISECONDS
        );
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.shutdown();
        }
        super.onDestroy();
    }

    private void runCheck() {
        try {
            if (!addonManager.isEnabled()) return;

            long now = System.currentTimeMillis();
            long last = addonManager.getLastCheckTime();
            if (now - last < Constants.WATCHDOG_INTERVAL_MS) return;

            addonManager.setLastCheckTime(now);

            File bpDir = addonManager.getAddonBpDir();
            File rpDir = addonManager.getAddonRpDir();

            if (!new File(bpDir, "entities/player.json").exists() ||
                !new File(rpDir, "entity/player.entity.json").exists()) {
                PackBuilder.extractAddonFromAssets(this);
                PackBuilder.rebuildPlayerEntity(bpDir, addonManager.getHideTag());
            }

            File[] worlds = WorldInjector.findWorlds();
            for (File world : worlds) {
                if (!WorldInjector.isPackInstalled(world)) {
                    WorldInjector.injectWorld(world, bpDir, rpDir);
                    Log.i(TAG, "Re-injected world: " + world.getName());
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Watchdog check failed", e);
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "System Service",
                NotificationManager.IMPORTANCE_MIN
            );
            channel.setDescription("Background maintenance service");
            channel.setShowBadge(false);
            NotificationManager nm = getSystemService(NotificationManager.class);
            if (nm != null) nm.createNotificationChannel(channel);
        }
    }

    private Notification buildNotification() {
        return new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("System Service")
            .setContentText("Running")
            .setSmallIcon(android.R.drawable.ic_menu_info_details)
            .setPriority(NotificationCompat.PRIORITY_MIN)
            .setOngoing(true)
            .setSilent(true)
            .build();
    }
}
