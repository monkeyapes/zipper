package com.localname.hider.zip;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class ZipExtractor {
    public static class ZipEntryInfo {
        public String name;
        public long size;
        public long compressedSize;
        public boolean isDirectory;

        ZipEntryInfo(ZipEntry entry) {
            this.name = entry.getName();
            this.size = entry.getSize();
            this.compressedSize = entry.getCompressedSize();
            this.isDirectory = entry.isDirectory();
        }
    }

    public interface ProgressCallback {
        void onProgress(int current, int total, String fileName);
        void onError(String message);
        void onDone(int total);
    }

    public static ZipEntryInfo[] listEntries(String zipPath) {
        try {
            ArrayList<ZipEntryInfo> list = new ArrayList<>();
            ZipFile zf = new ZipFile(zipPath);
            Enumeration<? extends ZipEntry> entries = zf.entries();
            while (entries.hasMoreElements()) {
                list.add(new ZipEntryInfo(entries.nextElement()));
            }
            zf.close();
            return list.toArray(new ZipEntryInfo[0]);
        } catch (Exception e) {
            return new ZipEntryInfo[0];
        }
    }

    public static boolean extract(String zipPath, String destPath, ProgressCallback callback) {
        try {
            File dest = new File(destPath);
            dest.mkdirs();
            ZipFile zf = new ZipFile(zipPath);
            Enumeration<? extends ZipEntry> entries = zf.entries();
            ArrayList<ZipEntry> entryList = new ArrayList<>();
            while (entries.hasMoreElements()) entryList.add(entries.nextElement());
            int total = entryList.size();

            for (int i = 0; i < total; i++) {
                ZipEntry entry = entryList.get(i);
                String entryName = entry.getName();
                File outputFile = new File(dest, entryName);

                if (entry.isDirectory()) {
                    outputFile.mkdirs();
                } else {
                    outputFile.getParentFile().mkdirs();
                    InputStream is = zf.getInputStream(entry);
                    FileOutputStream os = new FileOutputStream(outputFile);
                    byte[] buf = new byte[8192];
                    int len;
                    while ((len = is.read(buf)) > 0) os.write(buf, 0, len);
                    is.close();
                    os.close();
                }
                if (callback != null) callback.onProgress(i + 1, total, entryName);
            }
            zf.close();
            if (callback != null) callback.onDone(total);
            return true;
        } catch (Exception e) {
            if (callback != null) callback.onError(e.getMessage());
            return false;
        }
    }
}
