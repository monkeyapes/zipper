using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows.Forms;

namespace LocalNameControl;

static class Program
{
    [STAThread]
    static void Main(string[] args)
    {
        if (args.Length > 0 && IsMcFile(args[0]))
        {
            ForwardToLeviLauncher(args[0]);
            return;
        }

        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new MainForm());
    }

    static bool IsMcFile(string path)
    {
        var ext = Path.GetExtension(path)?.ToLower();
        return ext == ".mcaddon" || ext == ".mcpack" || ext == ".mcworld";
    }

    static void ForwardToLeviLauncher(string filePath)
    {
        string levi = FindLeviLauncher();
        if (levi != null)
        {
            try
            {
                Process.Start(levi, $"\"{filePath}\"");
                return;
            }
            catch { }
        }
        MessageBox.Show(
            "LeviLauncher not found.\n\nInstall it or place it in:\n" +
            string.Join("\n", LeviPaths),
            "LocalName", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }

    static readonly string[] LeviPaths =
    {
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "LeviLauncher", "LeviLauncher.exe"),
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "LeviLauncher", "Application", "LeviLauncher.exe"),
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "LeviLauncher", "LeviLauncher.exe"),
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "LeviLauncher", "LeviLauncher.exe"),
    };

    static string FindLeviLauncher()
    {
        foreach (var p in LeviPaths)
            if (File.Exists(p)) return p;
        return null;
    }
}
