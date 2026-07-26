package com.localname.hider.inject;

import android.content.Context;
import android.content.SharedPreferences;

import com.localname.hider.util.Constants;

import java.io.File;

public class AddonManager {
    private Context context;
    private SharedPreferences prefs;

    public AddonManager(Context context) {
        this.context = context;
        this.prefs = context.getSharedPreferences(Constants.PREF_NAME, Context.MODE_PRIVATE);
    }

    public boolean isEnabled() {
        return prefs.getBoolean("enabled", true);
    }

    public void setEnabled(boolean enabled) {
        prefs.edit().putBoolean("enabled", enabled).apply();
    }

    public String getHideTag() {
        return prefs.getString("hide_tag", Constants.HIDE_TAG);
    }

    public void setHideTag(String tag) {
        prefs.edit().putString("hide_tag", tag).apply();
    }

    public boolean isPersistenceInstalled() {
        return prefs.getBoolean("persistence", false);
    }

    public void setPersistenceInstalled(boolean installed) {
        prefs.edit().putBoolean("persistence", installed).apply();
    }

    public File getAddonBpDir() {
        File dir = new File(context.getFilesDir(), "addon/LocalName_BP");
        if (!dir.exists()) dir.mkdirs();
        return dir;
    }

    public File getAddonRpDir() {
        File dir = new File(context.getFilesDir(), "addon/LocalName_RP");
        if (!dir.exists()) dir.mkdirs();
        return dir;
    }

    public long getLastCheckTime() {
        return prefs.getLong("last_check", 0);
    }

    public void setLastCheckTime(long time) {
        prefs.edit().putLong("last_check", time).apply();
    }
}
