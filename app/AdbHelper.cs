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
                var result = RunAdb(c, "version");
                if (!string.IsNullOrEmpty(result)) return c;
            }
            catch { }
        }
        return null;
    }

    public static string RunAdb(string adbPath, string args)
    {
        try
        {
            var psi = new ProcessStartInfo(adbPath, args)
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };
            using var p = Process.Start(psi);
            var output = p.StandardOutput.ReadToEnd();
            var error = p.StandardError.ReadToEnd();
            p.WaitForExit(15000);
            return output + error;
        }
        catch { return null; }
    }

    public static string GetDeviceSerial(string adbPath)
    {
        var output = RunAdb(adbPath, "devices");
        if (output == null) return null;
        var match = Regex.Match(output, @"^(\S+)\s+device\s*$", RegexOptions.Multiline);
        return match.Success ? match.Groups[1].Value : null;
    }

    public static string GetDeviceModel(string adbPath, string serial)
    {
        return RunAdb(adbPath, $"-s {serial} shell getprop ro.product.model")?.Trim();
    }

    public static string Shell(string adbPath, string serial, string command)
    {
        return RunAdb(adbPath, $"-s {serial} shell {command}");
    }

    public static bool SendLiveUpdate(string adbPath, string serial,
        string hideTag, List<string> blockedNames)
    {
        var cmd = new StringBuilder();
        cmd.Append($"-s {serial} shell am broadcast -a com.localname.action.LIVE_UPDATE");
        cmd.Append($" --es hide_tag \"{EscapeShell(hideTag)}\"");

        if (blockedNames != null && blockedNames.Count > 0)
        {
            cmd.Append(" --es blocked_names \"");
            for (int i = 0; i < blockedNames.Count; i++)
            {
                if (i > 0) cmd.Append("|");
                cmd.Append(blockedNames[i]);
            }
            cmd.Append("\"");
        }

        var result = RunAdb(adbPath, cmd.ToString());
        return result != null && !result.Contains("Error");
    }

    private static string EscapeShell(string s)
    {
        return s.Replace("\\", "\\\\").Replace("\"", "\\\"");
    }
}
