package com.localname.hider.zip;

import android.app.AlertDialog;
import android.os.Bundle;
import android.os.Environment;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.localname.hider.zip.ZipExtractor.ZipEntryInfo;

import java.io.File;
import java.util.ArrayList;

public class ZipViewerActivity extends AppCompatActivity {
    private ListView listView;
    private TextView statusText;
    private ProgressBar progressBar;
    private Button extractBtn;
    private String currentZipPath;
    private ZipEntryInfo[] entries;
    private ArrayAdapter<String> adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(getResources().getIdentifier("activity_zip_viewer",
            "layout", getPackageName()));

        listView = findViewById(getResources().getIdentifier("zipList",
            "id", getPackageName()));
        statusText = findViewById(getResources().getIdentifier("zipStatus",
            "id", getPackageName()));
        progressBar = findViewById(getResources().getIdentifier("zipProgress",
            "id", getPackageName()));
        extractBtn = findViewById(getResources().getIdentifier("extractBtn",
            "id", getPackageName()));

        currentZipPath = getIntent().getStringExtra("zip_path");
        if (currentZipPath == null) {
            statusText.setText("No ZIP file specified");
            extractBtn.setEnabled(false);
            return;
        }

        loadZipContents();

        extractBtn.setOnClickListener(v -> extractZip());
    }

    private void loadZipContents() {
        statusText.setText("Loading: " + new File(currentZipPath).getName());
        entries = ZipExtractor.listEntries(currentZipPath);
        ArrayList<String> lines = new ArrayList<>();
        long totalSize = 0;
        for (ZipEntryInfo e : entries) {
            lines.add(e.name + "  (" + e.size + " bytes)");
            totalSize += e.size;
        }
        statusText.setText(entries.length + " entries, " + totalSize + " bytes total");
        adapter = new ArrayAdapter<>(this,
            android.R.layout.simple_list_item_1, lines);
        listView.setAdapter(adapter);
        progressBar.setVisibility(View.GONE);
    }

    private void extractZip() {
        String destPath = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
            + "/LocalName_Extracted";
        progressBar.setVisibility(View.VISIBLE);
        extractBtn.setEnabled(false);

        new Thread(() -> {
            boolean success = ZipExtractor.extract(currentZipPath, destPath,
                new ZipExtractor.ProgressCallback() {
                    @Override
                    public void onProgress(int current, int total, String fileName) {
                        runOnUiThread(() -> {
                            progressBar.setMax(total);
                            progressBar.setProgress(current);
                            statusText.setText("Extracting: " + fileName);
                        });
                    }

                    @Override
                    public void onError(String message) {
                        runOnUiThread(() -> {
                            Toast.makeText(ZipViewerActivity.this,
                                "Error: " + message, Toast.LENGTH_LONG).show();
                            progressBar.setVisibility(View.GONE);
                            extractBtn.setEnabled(true);
                        });
                    }

                    @Override
                    public void onDone(int total) {
                        runOnUiThread(() -> {
                            progressBar.setVisibility(View.GONE);
                            extractBtn.setEnabled(true);
                            statusText.setText("Extracted to: " + destPath);
                            Toast.makeText(ZipViewerActivity.this,
                                "Done! " + total + " files extracted", Toast.LENGTH_LONG).show();
                        });
                    }
                });
        }).start();
    }
}
