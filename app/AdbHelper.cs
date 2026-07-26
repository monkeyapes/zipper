using System;
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
                if (File.Exists(c) || c == "adb.exe")
                {
                    var result = RunAdb(c, "version");
                    if (!string.IsNullOrEmpty(result)) return c;
                }
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
            p.WaitForExit(10000);
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

    public static bool PushFile(string adbPath, string local, string remote)
    {
        var result = RunAdb(adbPath, $"push \"{local}\" \"{remote}\"");
        return result != null && !result.Contains("error");
    }

    public static bool SendBroadcast(string adbPath, string action, string extraKey, string extraValue)
    {
        var result = RunAdb(adbPath,
            $"shell am broadcast -a {action} --es {extraKey} \"{extraValue}\"");
        return result != null && !result.Contains("Error");
    }

    public static string Shell(string adbPath, string command)
    {
        return RunAdb(adbPath, $"shell {command}");
    }
}
