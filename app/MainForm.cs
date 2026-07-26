using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace LocalNameControl;

public class MainForm : Form
{
    private AppSettings _settings;
    private string _adbPath;
    private string _deviceSerial;

    private Label _lblDevice;
    private Label _lblConnection;
    private CheckBox _chkEnable;
    private CheckBox _chkHideName;
    private CheckBox _chkHideAvatar;
    private CheckBox _chkHideCape;
    private TextBox _txtTag;
    private CheckBox _chkAutoInject;
    private Label _lblWorldStatus;
    private Button _btnRefresh;
    private Button _btnApply;
    private Label _lblStatus;

    public MainForm()
    {
        _settings = AppSettings.Load();
        InitializeComponent();
        LoadSettings();
        FindAdbAsync();
    }

    private void InitializeComponent()
    {
        Text = "LocalName Control Center";
        Size = new Size(420, 400);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        BackColor = Color.FromArgb(30, 30, 30);
        ForeColor = Color.White;
        Font = new Font("Segoe UI", 10);

        var title = CreateLabel("LocalName Control Center", 12, 12, 380, 28, 14, true);
        title.TextAlign = ContentAlignment.MiddleCenter;
        Controls.Add(title);

        _lblDevice = CreateLabel("Device: —", 12, 50, 380, 20);
        Controls.Add(_lblDevice);

        _lblConnection = CreateLabel("Status: Not connected", 12, 72, 380, 20);
        Controls.Add(_lblConnection);

        var sep1 = CreateSeparator(100);
        Controls.Add(sep1);

        _chkEnable = CreateCheckBox("Master Toggle", 12, 110);
        _chkEnable.CheckedChanged += (_, _) => UpdateEnabledState();
        Controls.Add(_chkEnable);

        _chkHideName = CreateCheckBox("Hide Name", 30, 138);
        Controls.Add(_chkHideName);

        _chkHideAvatar = CreateCheckBox("Hide Avatar", 30, 162);
        Controls.Add(_chkHideAvatar);

        _chkHideCape = CreateCheckBox("Hide Cape", 30, 186);
        Controls.Add(_chkHideCape);

        var lblTagLabel = CreateLabel("Obfuscation Tag:", 12, 216, 120, 22);
        Controls.Add(lblTagLabel);
        _txtTag = new TextBox
        {
            Location = new Point(140, 214),
            Size = new Size(250, 24),
            BackColor = Color.FromArgb(50, 50, 50),
            ForeColor = Color.White,
            BorderStyle = BorderStyle.FixedSingle,
            Text = _settings.ObfuscationTag
        };
        Controls.Add(_txtTag);

        _chkAutoInject = CreateCheckBox("Auto-inject on connect", 12, 244);
        Controls.Add(_chkAutoInject);

        var sep2 = CreateSeparator(272);
        Controls.Add(sep2);

        _lblWorldStatus = CreateLabel("Worlds: —", 12, 280, 380, 20);
        Controls.Add(_lblWorldStatus);

        _btnRefresh = new Button
        {
            Text = "Refresh Device",
            Location = new Point(12, 310),
            Size = new Size(180, 32),
            BackColor = Color.FromArgb(60, 60, 60),
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat
        };
        _btnRefresh.Click += async (_, _) => { _btnRefresh.Enabled = false; await System.Threading.Tasks.Task.Run(() => FindAdbAsync()); _btnRefresh.Enabled = true; };
        Controls.Add(_btnRefresh);

        _btnApply = new Button
        {
            Text = "Apply && Inject",
            Location = new Point(210, 310),
            Size = new Size(180, 32),
            BackColor = Color.FromArgb(0, 120, 200),
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat
        };
        _btnApply.Click += BtnApply_Click;
        Controls.Add(_btnApply);

        _lblStatus = CreateLabel("Ready", 12, 348, 380, 16, 9);
        _lblStatus.ForeColor = Color.FromArgb(150, 150, 150);
        Controls.Add(_lblStatus);
    }

    private Label CreateLabel(string text, int x, int y, int w, int h, float fontSize = 10, bool bold = false)
    {
        return new Label
        {
            Text = text,
            Location = new Point(x, y),
            Size = new Size(w, h),
            ForeColor = Color.White,
            BackColor = Color.Transparent,
            Font = new Font("Segoe UI", fontSize, bold ? FontStyle.Bold : FontStyle.Regular)
        };
    }

    private CheckBox CreateCheckBox(string text, int x, int y)
    {
        return new CheckBox
        {
            Text = text,
            Location = new Point(x, y),
            Size = new Size(180, 24),
            ForeColor = Color.White,
            BackColor = Color.Transparent,
            FlatStyle = FlatStyle.Flat
        };
    }

    private Panel CreateSeparator(int y)
    {
        return new Panel
        {
            Location = new Point(12, y),
            Size = new Size(380, 1),
            BackColor = Color.FromArgb(60, 60, 60)
        };
    }

    private void LoadSettings()
    {
        _chkEnable.Checked = _settings.Enabled;
        _chkHideName.Checked = _settings.HideName;
        _chkHideAvatar.Checked = _settings.HideAvatar;
        _chkHideCape.Checked = _settings.HideCape;
        _txtTag.Text = _settings.ObfuscationTag;
        _chkAutoInject.Checked = _settings.AutoInject;
        UpdateEnabledState();
    }

    private void UpdateEnabledState()
    {
        bool enabled = _chkEnable.Checked;
        _chkHideName.Enabled = enabled;
        _chkHideAvatar.Enabled = enabled;
        _chkHideCape.Enabled = enabled;
        _txtTag.Enabled = enabled;
        _btnApply.Enabled = enabled;
    }

    private void FindAdbAsync()
    {
        SetStatus("Looking for ADB...");
        _adbPath = AdbHelper.FindAdb();
        if (_adbPath == null)
        {
            _lblConnection.Text = "Status: ADB not found";
            _lblDevice.Text = "Device: —";
            _lblWorldStatus.Text = "Worlds: —";
            SetStatus("Install Android SDK platform-tools");
            _deviceSerial = null;
            return;
        }

        _deviceSerial = AdbHelper.GetDeviceSerial(_adbPath);
        if (_deviceSerial == null)
        {
            _lblConnection.Text = "Status: No device connected";
            _lblDevice.Text = "Device: —";
            _lblWorldStatus.Text = "Worlds: —";
            SetStatus("Connect an Android device via USB");
            return;
        }

        var deviceInfo = AdbHelper.Shell(_adbPath, "getprop ro.product.model")?.Trim();
        _lblDevice.Text = $"Device: {deviceInfo ?? _deviceSerial}";
        _lblConnection.Text = "Status: Connected";
        SetStatus($"Connected to {_deviceSerial}");

        CountInjectedWorlds();

        if (_chkAutoInject.Checked && _chkEnable.Checked)
        {
            ApplySettings();
        }
    }

    private void CountInjectedWorlds()
    {
        if (_deviceSerial == null || _adbPath == null) return;
        var result = AdbHelper.Shell(_adbPath, "ls /sdcard/games/com.mojang/MinecraftWorlds/ 2>/dev/null | wc -l");
        int total = 0;
        int.TryParse(result?.Trim(), out total);
        _lblWorldStatus.Text = $"Worlds detected: {total}";
    }

    private void BtnApply_Click(object sender, EventArgs e)
    {
        SaveSettings();
        ApplySettings();
    }

    private void SaveSettings()
    {
        _settings.Enabled = _chkEnable.Checked;
        _settings.HideName = _chkHideName.Checked;
        _settings.HideAvatar = _chkHideAvatar.Checked;
        _settings.HideCape = _chkHideCape.Checked;
        _settings.ObfuscationTag = _txtTag.Text;
        _settings.AutoInject = _chkAutoInject.Checked;
        _settings.Save();
    }

    private void ApplySettings()
    {
        if (_deviceSerial == null || _adbPath == null)
        {
            SetStatus("No device connected");
            return;
        }

        SetStatus("Applying settings...");

        string tag = _settings.Enabled ? _settings.ObfuscationTag : "";

        var sent = AdbHelper.SendBroadcast(_adbPath,
            "com.localname.action.LIVE_UPDATE",
            "hide_tag", tag);

        if (sent)
            SetStatus("Settings applied via live update");
        else
            SetStatus("Broadcast failed (APK may not be installed)");

        CountInjectedWorlds();
    }

    private void SetStatus(string msg)
    {
        if (InvokeRequired)
        {
            Invoke(() => _lblStatus.Text = msg);
        }
        else
        {
            _lblStatus.Text = msg;
        }
    }
}
