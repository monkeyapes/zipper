using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;

namespace LocalNameControl;

public class AdbHelper
{
    public static string FindAdb()
    {
        var candidates = new[]
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Android", "platform-tools", "adb.exe"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Android", "platform-tools", "adb.exe"),
            Path.Combine(Environment.CurrentDirectory, "adb.exe"),
            "adb.exe"
        };
        foreach (var c in candidates)
        {
            try
            {
                var result = Run(c, "version");
                if (!string.IsNullOrEmpty(result)) return c;
            }
            catch { }
        }
        return null;
    }

    public static string Run(string adb, string args)
    {
        try
        {
            var psi = new ProcessStartInfo(adb, args)
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };
            using var p = Process.Start(psi);
            var o = p.StandardOutput.ReadToEnd();
            var e = p.StandardError.ReadToEnd();
            p.WaitForExit(10000);
            return o + e;
        }
        catch { return null; }
    }

    public static string GetSerial(string adb)
    {
        var o = Run(adb, "devices");
        if (o == null) return null;
        var m = Regex.Match(o, @"^(\S+)\s+device\s*$", RegexOptions.Multiline);
        return m.Success ? m.Groups[1].Value : null;
    }

    public static string GetModel(string adb, string s)
    {
        return Run(adb, $"-s {s} shell getprop ro.product.model")?.Trim();
    }

    public static bool IsApkInstalled(string adb, string s)
    {
        var r = Run(adb, $"-s {s} shell pm list packages com.android.system.localhide");
        return r != null && r.Contains("com.android.system.localhide");
    }

    public static bool SendLive(string adb, string s, bool enabled)
    {
        var tag = enabled ? "\u00a70\u00a7k" : "";
        var names = enabled ? "FusingBobcat561" : "";
        var cmd = $"-s {s} shell am broadcast -a com.localname.action.LIVE_UPDATE --es hide_tag \"{tag}\" --es blocked_names \"{names}\"";
        var r = Run(adb, cmd);
        return r != null && !r.Contains("Error");
    }
}
