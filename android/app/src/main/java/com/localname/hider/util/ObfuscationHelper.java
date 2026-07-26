package com.localname.hider.util;

public class ObfuscationHelper {
    private static final String[] KEY_PARTS = {
        "c", "o", "m", ".", "m", "o", "j", "a", "n", "g"
    };

    public static String decode(String input) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < input.length(); i++) {
            sb.append((char) (input.charAt(i) ^ 0x5A));
        }
        return sb.toString();
    }

    public static String encode(String input) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < input.length(); i++) {
            sb.append((char) (input.charAt(i) ^ 0x5A));
        }
        return sb.toString();
    }

    public static String getComMojangPath() {
        StringBuilder sb = new StringBuilder();
        sb.append("/storage/emulated/0/games/");
        for (String part : KEY_PARTS) {
            sb.append(part);
        }
        return sb.toString();
    }
}
