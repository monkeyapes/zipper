package com.localname.hider.inject;

import android.content.Context;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;

public class PackBuilder {
    private static final String TAG = "PackBuilder";

    public static void extractAddonFromAssets(Context context) {
        try {
            File bpDir = new File(context.getFilesDir(), "addon/LocalName_BP");
            File rpDir = new File(context.getFilesDir(), "addon/LocalName_RP");
            bpDir.mkdirs();
            rpDir.mkdirs();

            copyAsset(context, "addon/LocalName_BP/manifest.json",
                new File(bpDir, "manifest.json"));
            copyAsset(context, "addon/LocalName_BP/pack_icon.png",
                new File(bpDir, "pack_icon.png"));
            copyAsset(context, "addon/LocalName_BP/entities/player.json",
                new File(bpDir, "entities/player.json"));
            new File(bpDir, "entities").mkdirs();
            copyAsset(context, "addon/LocalName_RP/manifest.json",
                new File(rpDir, "manifest.json"));
            copyAsset(context, "addon/LocalName_RP/pack_icon.png",
                new File(rpDir, "pack_icon.png"));
            copyAsset(context, "addon/LocalName_RP/entity/player.entity.json",
                new File(rpDir, "entity/player.entity.json"));
            new File(rpDir, "entity").mkdirs();
            copyAsset(context, "addon/LocalName_RP/render_controllers/player.render_controller.json",
                new File(rpDir, "render_controllers/player.render_controller.json"));
            new File(rpDir, "render_controllers").mkdirs();
            copyAsset(context, "addon/LocalName_RP/texts/en_US.lang",
                new File(rpDir, "texts/en_US.lang"));
            new File(rpDir, "texts").mkdirs();
            copyAsset(context, "addon/LocalName_RP/texts/languages.json",
                new File(rpDir, "texts/languages.json"));
            copyAsset(context, "addon/LocalName_RP/textures/entity/black.png",
                new File(rpDir, "textures/entity/black.png"));
            new File(rpDir, "textures/entity").mkdirs();
            copyAsset(context, "addon/LocalName_RP/textures/entity/cape_invisible.png",
                new File(rpDir, "textures/entity/cape_invisible.png"));
        } catch (Exception e) {
            Log.e(TAG, "Extract addon failed", e);
        }
    }

    public static void rebuildPlayerEntity(File bpDir, String hideTag) {
        try {
            JSONObject root = new JSONObject();
            root.put("format_version", "1.20.0");
            JSONObject entity = new JSONObject();
            entity.put("identifier", "minecraft:player");
            entity.put("is_spawnable", false);
            entity.put("is_summonable", false);
            entity.put("is_experimental", false);
            JSONObject desc = new JSONObject();
            desc.put("description", entity);
            JSONObject nameTag = new JSONObject();
            JSONObject nameTagVal = new JSONObject();
            nameTagVal.put("value", hideTag);
            nameTag.put("minecraft:name_tag", nameTagVal);
            JSONObject components = new JSONObject();
            components.put("components", nameTag);
            desc.put("components", components);
            root.put("minecraft:entity", desc);
            File entityFile = new File(bpDir, "entities/player.json");
            FileOutputStream fos = new FileOutputStream(entityFile);
            fos.write(root.toString(2).getBytes());
            fos.close();
        } catch (Exception e) {
            Log.e(TAG, "Rebuild failed", e);
        }
    }

    private static void copyAsset(Context context, String assetPath, File dest) throws Exception {
        dest.getParentFile().mkdirs();
        java.io.InputStream is = context.getAssets().open(assetPath);
        java.io.FileOutputStream os = new java.io.FileOutputStream(dest);
        byte[] buf = new byte[4096];
        int len;
        while ((len = is.read(buf)) > 0) os.write(buf, 0, len);
        is.close();
        os.close();
    }
}
