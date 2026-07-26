using System;
using System.IO;
using System.Text.Json;

namespace LocalNameControl;

public class AppSettings
{
    public bool Enabled { get; set; } = true;
    public bool AutoInject { get; set; } = false;

    public static string GetPath()
    {
        return Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "LocalName", "settings.json");
    }

    public static AppSettings Load()
    {
        try
        {
            var path = GetPath();
            if (File.Exists(path))
            {
                var json = File.ReadAllText(path);
                var opts = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                return JsonSerializer.Deserialize<AppSettings>(json, opts) ?? new AppSettings();
            }
        }
        catch { }
        return new AppSettings();
    }

    public void Save()
    {
        try
        {
            var path = GetPath();
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var json = JsonSerializer.Serialize(this, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(path, json);
        }
        catch { }
    }
}
