using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace LocalNameControl;

static class Program
{
    [STAThread]
    static void Main(string[] args)
    {
        if (args.Length > 0 && IsMcFile(args[0]))
        {
            try
            {
                Process.Start(new ProcessStartInfo(args[0]) { UseShellExecute = true });
            }
            catch
            {
                MessageBox.Show("Could not open file.\nMake sure Minecraft Bedrock is installed.",
                    "LocalName", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
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
}
