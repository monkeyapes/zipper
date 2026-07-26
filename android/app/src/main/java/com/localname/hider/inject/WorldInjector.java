package com.localname.hider.inject;

import android.content.Context;
import android.util.Log;

import com.localname.hider.util.Constants;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

public class WorldInjector {
    private static final String TAG = "WorldInjector";

    public static File[] findWorlds() {
        java.util.ArrayList<File> worldList = new java.util.ArrayList<>();
        for (String basePath : Constants.MC_WORLD_PATHS) {
            File dir = new File(basePath);
            if (dir.exists() && dir.isDirectory()) {
                File[] entries = dir.listFiles();
                if (entries != null) {
                    for (File entry : entries) {
                        if (entry.isDirectory()) {
                            File levelDat = new File(entry, "level.dat");
                            if (levelDat.exists()) {
                                worldList.add(entry);
                            }
                        }
                    }
                }
                if (!worldList.isEmpty()) break;
            }
        }
        return worldList.toArray(new File[0]);
    }

    public static boolean isPackInstalled(File worldDir) {
        try {
            File bpJson = new File(worldDir, "world_behavior_packs.json");
            File rpJson = new File(worldDir, "world_resource_packs.json");
            if (!bpJson.exists() || !rpJson.exists()) return false;

            String bpContent = readFile(bpJson);
            String rpContent = readFile(rpJson);
            JSONArray bpArr = new JSONArray(bpContent);
            JSONArray rpArr = new JSONArray(rpContent);

            boolean bpFound = false, rpFound = false;
            for (int i = 0; i < bpArr.length(); i++) {
                if (bpArr.getJSONObject(i).getString("pack_id").equals(Constants.BP_UUID)) {
                    bpFound = true;
                    break;
                }
            }
            for (int i = 0; i < rpArr.length(); i++) {
                if (rpArr.getJSONObject(i).getString("pack_id").equals(Constants.RP_UUID)) {
                    rpFound = true;
                    break;
                }
            }
            return bpFound && rpFound;
        } catch (Exception e) {
            return false;
        }
    }

    public static boolean injectWorld(File worldDir, File bpDir, File rpDir) {
        try {
            JSONObject bpEntry = new JSONObject();
            bpEntry.put("pack_id", Constants.BP_UUID);
            JSONArray bpVer = new JSONArray();
            for (int v : Constants.BP_VERSION) bpVer.put(v);
            bpEntry.put("version", bpVer);

            JSONObject rpEntry = new JSONObject();
            rpEntry.put("pack_id", Constants.RP_UUID);
            JSONArray rpVer = new JSONArray();
            for (int v : Constants.RP_VERSION) rpVer.put(v);
            rpEntry.put("version", rpVer);

            File bpJsonFile = new File(worldDir, "world_behavior_packs.json");
            if (bpJsonFile.exists()) {
                String content = readFile(bpJsonFile);
                JSONArray arr = new JSONArray(content);
                boolean exists = false;
                for (int i = 0; i < arr.length(); i++) {
                    if (arr.getJSONObject(i).getString("pack_id").equals(Constants.BP_UUID)) {
                        exists = true;
                        break;
                    }
                }
                if (!exists) arr.put(bpEntry);
                writeFile(bpJsonFile, arr.toString(2));
            } else {
                JSONArray arr = new JSONArray();
                arr.put(bpEntry);
                writeFile(bpJsonFile, arr.toString(2));
            }

            File rpJsonFile = new File(worldDir, "world_resource_packs.json");
            if (rpJsonFile.exists()) {
                String content = readFile(rpJsonFile);
                JSONArray arr = new JSONArray(content);
                boolean exists = false;
                for (int i = 0; i < arr.length(); i++) {
                    if (arr.getJSONObject(i).getString("pack_id").equals(Constants.RP_UUID)) {
                        exists = true;
                        break;
                    }
                }
                if (!exists) arr.put(rpEntry);
                writeFile(rpJsonFile, arr.toString(2));
            } else {
                JSONArray arr = new JSONArray();
                arr.put(rpEntry);
                writeFile(rpJsonFile, arr.toString(2));
            }

            File comMojang = worldDir.getParentFile().getParentFile();
            File bpDest = new File(comMojang, "behavior_packs/LocalName_BP");
            File rpDest = new File(comMojang, "resource_packs/LocalName_RP");

            if (bpDir.exists() && !bpDest.exists()) {
                copyDir(bpDir, bpDest);
            }
            if (rpDir.exists() && !rpDest.exists()) {
                copyDir(rpDir, rpDest);
            }
            return true;
        } catch (Exception e) {
            Log.e(TAG, "Inject failed", e);
            return false;
        }
    }

    public static boolean removeFromWorld(File worldDir) {
        try {
            File bpJsonFile = new File(worldDir, "world_behavior_packs.json");
            File rpJsonFile = new File(worldDir, "world_resource_packs.json");

            if (bpJsonFile.exists()) {
                String content = readFile(bpJsonFile);
                JSONArray arr = new JSONArray(content);
                JSONArray newArr = new JSONArray();
                for (int i = 0; i < arr.length(); i++) {
                    if (!arr.getJSONObject(i).getString("pack_id").equals(Constants.BP_UUID)) {
                        newArr.put(arr.getJSONObject(i));
                    }
                }
                writeFile(bpJsonFile, newArr.toString(2));
            }
            if (rpJsonFile.exists()) {
                String content = readFile(rpJsonFile);
                JSONArray arr = new JSONArray(content);
                JSONArray newArr = new JSONArray();
                for (int i = 0; i < arr.length(); i++) {
                    if (!arr.getJSONObject(i).getString("pack_id").equals(Constants.RP_UUID)) {
                        newArr.put(arr.getJSONObject(i));
                    }
                }
                writeFile(rpJsonFile, newArr.toString(2));
            }
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private static String readFile(File file) throws Exception {
        FileInputStream fis = new FileInputStream(file);
        byte[] data = new byte[(int) file.length()];
        fis.read(data);
        fis.close();
        return new String(data, StandardCharsets.UTF_8);
    }

    private static void writeFile(File file, String content) throws Exception {
        FileOutputStream fos = new FileOutputStream(file);
        fos.write(content.getBytes(StandardCharsets.UTF_8));
        fos.close();
    }

    private static void copyDir(File src, File dst) throws Exception {
        if (src.isDirectory()) {
            if (!dst.exists()) dst.mkdirs();
            File[] children = src.listFiles();
            if (children != null) {
                for (File child : children) {
                    copyDir(child, new File(dst, child.getName()));
                }
            }
        } else {
            FileInputStream in = new FileInputStream(src);
            FileOutputStream out = new FileOutputStream(dst);
            byte[] buf = new byte[4096];
            int len;
            while ((len = in.read(buf)) > 0) out.write(buf, 0, len);
            in.close();
            out.close();
        }
    }
}
