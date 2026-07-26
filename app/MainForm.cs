using System;
using System.Drawing;
using System.Windows.Forms;

namespace LocalNameControl;

public class MainForm : Form
{
    private AppSettings _settings;
    private string _adbPath;
    private string _serial;

    private Panel _dotDevice;
    private Panel _dotAddon;
    private Label _lblDevice;
    private Label _lblAddon;
    private Label _lblTarget;
    private CheckBox _chkOn;
    private CheckBox _chkAuto;
    private Button _btnApply;
    private Label _lblStatus;
    private Timer _refreshTimer;

    private Color _green = Color.FromArgb(0, 200, 80);
    private Color _red = Color.FromArgb(210, 50, 50);
    private Color _gray = Color.FromArgb(60, 60, 66);
    private Color _bg = Color.FromArgb(20, 20, 24);
    private Color _panel = Color.FromArgb(30, 30, 36);
    private Color _text = Color.FromArgb(220, 220, 225);
    private Color _dim = Color.FromArgb(140, 140, 148);

    public MainForm()
    {
        _settings = AppSettings.Load();
        InitializeComponent();
        LoadSettings();
        Shown += (_, _) => RefreshAll();
        _refreshTimer = new Timer { Interval = 5000 };
        _refreshTimer.Tick += (_, _) => RefreshAll();
        _refreshTimer.Start();
    }

    private void InitializeComponent()
    {
        Text = "LocalName";
        Size = new Size(360, 340);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        BackColor = _bg;
        ForeColor = _text;
        Font = new Font("Segoe UI", 10);

        // Device status row
        var y = 16;
        _dotDevice = new Panel { Location = new Point(16, y + 4), Size = new Size(12, 12), BackColor = _gray };
        Controls.Add(_dotDevice);
        _lblDevice = new Label
        {
            Text = "Device: \u2014",
            Location = new Point(34, y), Size = new Size(300, 22),
            ForeColor = _dim, BackColor = Color.Transparent,
            Font = new Font("Segoe UI", 10, FontStyle.Bold)
        };
        Controls.Add(_lblDevice);
        y += 28;

        // Addon status row
        _dotAddon = new Panel { Location = new Point(16, y + 4), Size = new Size(12, 12), BackColor = _gray };
        Controls.Add(_dotAddon);
        _lblAddon = new Label
        {
            Text = "Addon: \u2014",
            Location = new Point(34, y), Size = new Size(300, 22),
            ForeColor = _dim, BackColor = Color.Transparent
        };
        Controls.Add(_lblAddon);
        y += 28;

        // Target player
        _lblTarget = new Label
        {
            Text = "Target: FusingBobcat561",
            Location = new Point(16, y), Size = new Size(300, 22),
            ForeColor = Color.FromArgb(100, 180, 255), BackColor = Color.Transparent,
            Font = new Font("Segoe UI", 9, FontStyle.Italic)
        };
        Controls.Add(_lblTarget);
        y += 34;

        // Separator
        Controls.Add(new Panel { Location = new Point(16, y), Size = new Size(310, 1), BackColor = Color.FromArgb(50, 50, 56) });
        y += 16;

        // Master toggle
        _chkOn = CBox("Active", 16, y);
        _chkOn.CheckedChanged += (_, _) => UpdateUI();
        Controls.Add(_chkOn);
        y += 30;

        // Auto inject
        _chkAuto = CBox("Auto-inject on connect", 16, y);
        Controls.Add(_chkAuto);
        y += 36;

        // Buttons
        _btnApply = new Button
        {
            Text = "Apply",
            Location = new Point(220, y), Size = new Size(100, 30),
            BackColor = Color.FromArgb(0, 130, 230), ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat, FlatAppearance = { BorderSize = 0 },
            Font = new Font("Segoe UI", 10, FontStyle.Bold), Cursor = Cursors.Hand,
            UseVisualStyleBackColor = false
        };
        _btnApply.Click += (_, _) => ApplyNow();
        Controls.Add(_btnApply);

        y += 42;

        // Status bar
        _lblStatus = new Label
        {
            Text = "Ready",
            Location = new Point(16, y), Size = new Size(320, 18),
            ForeColor = _dim, BackColor = Color.Transparent, Font = new Font("Segoe UI", 9)
        };
        Controls.Add(_lblStatus);
    }

    private CheckBox CBox(string text, int x, int y)
    {
        return new CheckBox
        {
            Text = text, Location = new Point(x, y), Size = new Size(180, 24),
            ForeColor = _text, BackColor = Color.Transparent
        };
    }

    private void LoadSettings()
    {
        _chkOn.Checked = _settings.Enabled;
        _chkAuto.Checked = _settings.AutoInject;
        UpdateUI();
    }

    private void UpdateUI()
    {
        _btnApply.Enabled = _chkOn.Checked;
    }

    private void RefreshAll()
    {
        _adbPath = AdbHelper.FindAdb();
        if (_adbPath == null)
        {
            SetDevice(false, "ADB not found");
            SetAddon(false);
            return;
        }

        _serial = AdbHelper.GetSerial(_adbPath);
        if (_serial == null)
        {
            SetDevice(false, "No device");
            SetAddon(false);
            return;
        }

        var model = AdbHelper.GetModel(_adbPath, _serial) ?? _serial;
        SetDevice(true, model);

        var apkOk = AdbHelper.IsApkInstalled(_adbPath, _serial);
        SetAddon(apkOk);

        if (_chkAuto.Checked && _chkOn.Checked && apkOk)
            ApplyNow();
    }

    private void SetDevice(bool ok, string text)
    {
        UI(() => { _dotDevice.BackColor = ok ? _green : _red; _lblDevice.Text = $"Device: {text}"; });
    }

    private void SetAddon(bool ok)
    {
        UI(() => { _dotAddon.BackColor = ok ? _green : _red; _lblAddon.Text = ok ? "Addon: Active" : "Addon: Not installed"; });
    }

    private void ApplyNow()
    {
        Save();
        if (_serial == null || _adbPath == null) { SetStatus("No device"); return; }
        SetStatus("Sending...");
        var ok = AdbHelper.SendLive(_adbPath, _serial, _chkOn.Checked);
        SetStatus(ok ? "Applied \u2014 FusingBobcat561 is now " + (_chkOn.Checked ? "hidden" : "visible") : "Failed");
    }

    private void Save()
    {
        _settings.Enabled = _chkOn.Checked;
        _settings.AutoInject = _chkAuto.Checked;
        _settings.Save();
    }

    private void SetStatus(string m) => UI(() => _lblStatus.Text = m);

    private void UI(Action a)
    {
        if (IsHandleCreated && InvokeRequired) BeginInvoke(a);
        else if (IsHandleCreated) a();
    }
}
