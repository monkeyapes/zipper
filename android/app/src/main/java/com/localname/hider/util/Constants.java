package com.localname.hider.util;

public class Constants {
    public static final String PACKAGE_NAME = "com.android.system.localhide";
    public static final String BP_UUID = "a7f8e3d2-1b4c-5e6d-9f0a-8b7c6d5e4f3a";
    public static final String RP_UUID = "c9d0e1f2-3a4b-5c6d-7e8f-9a0b1c2d3e4f";
    public static final String HIDE_TAG = "\u00a70\u00a7k";
    public static final int[] BP_VERSION = {1, 0, 0};
    public static final int[] RP_VERSION = {1, 0, 0};
    public static final String PREF_NAME = "localname_config";
    public static final long WATCHDOG_INTERVAL_MS = 86400000L;
    public static final String INTENT_TOGGLE = "com.localname.action.TOGGLE";
    public static final String INTENT_CHECK = "com.localname.action.CHECK_NOW";
    public static final String ASSETS_BP = "addon/LocalName_BP";
    public static final String ASSETS_RP = "addon/LocalName_RP";

    public static final String[] MC_WORLD_PATHS = {
        "/storage/emulated/0/games/com.mojang/minecraftWorlds",
        "/storage/emulated/0/Android/data/com.mojang.minecraftpe/files/games/com.mojang/minecraftWorlds",
        "/sdcard/games/com.mojang/minecraftWorlds"
    };
}
