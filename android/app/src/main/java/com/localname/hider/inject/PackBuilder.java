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

    public static void rebuildPlayerEntity(File bpDir, String hideTag, String[] blockedNames) {
        try {
            JSONObject root = new JSONObject();
            root.put("format_version", "1.132.1");
            JSONObject entity = new JSONObject();
            JSONObject desc = new JSONObject();
            desc.put("identifier", "minecraft:player");
            desc.put("is_spawnable", false);
            desc.put("is_summonable", false);
            desc.put("is_experimental", false);
            entity.put("description", desc);

            if (blockedNames != null && blockedNames.length > 0) {
                JSONObject hiddenGroup = new JSONObject();
                JSONObject nameTag = new JSONObject();
                nameTag.put("value", hideTag);
                hiddenGroup.put("minecraft:name_tag", nameTag);
                JSONObject cg = new JSONObject();
                cg.put("localname:hidden", hiddenGroup);

                JSONArray triggers = new JSONArray();
                for (String name : blockedNames) {
                    JSONObject filter = new JSONObject();
                    filter.put("test", "name");
                    filter.put("subject", "self");
                    filter.put("operator", "equals");
                    filter.put("value", name.trim());
                    JSONObject trigger = new JSONObject();
                    trigger.put("filters", filter);
                    trigger.put("event", "localname:hide");
                    triggers.put(trigger);
                }
                JSONObject sensor = new JSONObject();
                sensor.put("triggers", triggers);
                JSONObject envSensor = new JSONObject();
                envSensor.put("minecraft:environment_sensor", sensor);

                JSONObject comps = new JSONObject();
                JSONObject defaultTag = new JSONObject();
                defaultTag.put("value", "");
                comps.put("minecraft:name_tag", defaultTag);
                comps.put("minecraft:environment_sensor", envSensor);

                JSONObject hideEvent = new JSONObject();
                JSONArray addGroup = new JSONArray();
                addGroup.put("localname:hidden");
                JSONObject add = new JSONObject();
                add.put("component_groups", addGroup);
                hideEvent.put("add", add);
                JSONObject events = new JSONObject();
                events.put("localname:hide", hideEvent);

                entity.put("component_groups", cg);
                entity.put("components", comps);
                entity.put("events", events);
            } else {
                JSONObject comps = new JSONObject();
                JSONObject nameTag = new JSONObject();
                nameTag.put("value", hideTag);
                comps.put("minecraft:name_tag", nameTag);
                entity.put("components", comps);
            }

            root.put("minecraft:entity", entity);
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
