using System;
using System.Drawing;
using System.Windows.Forms;

namespace LocalNameControl;

public class MainForm : Form
{
    private AppSettings _settings;
    private string _adbPath;
    private string _deviceSerial;

    private Label _lblDevice;
    private Label _lblStatus;
    private Label _lblWorlds;
    private Panel _statusDot;

    private CheckBox _chkMaster;
    private CheckBox _chkName;
    private CheckBox _chkAvatar;
    private CheckBox _chkCape;
    private TextBox _txtTag;

    private RadioButton _radioAll;
    private RadioButton _radioSpecific;
    private ListBox _lstBlocked;
    private TextBox _txtName;
    private Button _btnAdd;
    private Button _btnRemove;

    private CheckBox _chkAuto;
    private Button _btnRefresh;
    private Button _btnApply;

    private Color _bg = Color.FromArgb(24, 24, 28);
    private Color _panel = Color.FromArgb(32, 32, 38);
    private Color _text = Color.FromArgb(220, 220, 225);
    private Color _dim = Color.FromArgb(140, 140, 148);
    private Color _accent = Color.FromArgb(0, 130, 230);
    private Color _green = Color.FromArgb(0, 190, 90);
    private Color _red = Color.FromArgb(210, 50, 50);

    public MainForm()
    {
        _settings = AppSettings.Load();
        InitializeComponent();
        LoadSettings();
        Shown += (_, _) => RefreshDevice();
    }

    private void InitializeComponent()
    {
        Text = "LocalName Control";
        Size = new Size(520, 560);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        BackColor = _bg;
        ForeColor = _text;
        Font = new Font("Segoe UI", 10);

        // Device status
        var y = 12;

        _statusDot = new Panel { Location = new Point(16, y + 6), Size = new Size(10, 10), BackColor = _red };
        Controls.Add(_statusDot);

        _lblDevice = new Label
        {
            Text = "No device connected",
            Location = new Point(32, y), Size = new Size(460, 22),
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            ForeColor = _dim, BackColor = Color.Transparent
        };
        Controls.Add(_lblDevice);

        y += 34;

        // Master toggle
        var gbMaster = GroupBox(y, 48, "Controls");
        _chkMaster = CheckBox("Master Toggle", 16, 14, gbMaster);
        _chkMaster.CheckedChanged += (_, _) => UpdateEnabled();
        Controls.Add(gbMaster);
        y += 56;

        // Hide options
        var gbHide = GroupBox(y, 80, "Hide");
        _chkName = CheckBox("Player Name", 16, 14, gbHide);
        _chkAvatar = CheckBox("Avatar Skin", 150, 14, gbHide);
        _chkCape = CheckBox("Cape", 290, 14, gbHide);
        var lbl = new Label
        {
            Text = "Tag:",
            Location = new Point(16, 44), Size = new Size(40, 22),
            ForeColor = _dim, BackColor = Color.Transparent, Font = new Font("Segoe UI", 9)
        };
        gbHide.Controls.Add(lbl);
        _txtTag = new TextBox
        {
            Location = new Point(56, 42), Size = new Size(280, 22),
            BackColor = Color.FromArgb(40, 40, 46), ForeColor = _text,
            BorderStyle = BorderStyle.FixedSingle, Font = new Font("Consolas", 10),
            Text = _settings.ObfuscationTag
        };
        gbHide.Controls.Add(_txtTag);
        Controls.Add(gbHide);
        y += 88;

        // Target mode + blocked list
        var gbTarget = GroupBox(y, 200, "Target");
        _radioAll = new RadioButton
        {
            Text = "All players",
            Location = new Point(16, 14), Size = new Size(130, 22),
            ForeColor = _text, BackColor = Color.Transparent, Checked = true
        };
        _radioSpecific = new RadioButton
        {
            Text = "Specific players",
            Location = new Point(150, 14), Size = new Size(150, 22),
            ForeColor = _text, BackColor = Color.Transparent
        };
        _radioSpecific.CheckedChanged += (_, _) => UpdateBlocked();
        gbTarget.Controls.Add(_radioAll);
        gbTarget.Controls.Add(_radioSpecific);

        _lstBlocked = new ListBox
        {
            Location = new Point(16, 42), Size = new Size(270, 140),
            BackColor = Color.FromArgb(40, 40, 46), ForeColor = _text,
            BorderStyle = BorderStyle.FixedSingle, Sorted = true
        };
        gbTarget.Controls.Add(_lstBlocked);

        _txtName = new TextBox
        {
            Location = new Point(298, 42), Size = new Size(92, 22),
            BackColor = Color.FromArgb(40, 40, 46), ForeColor = _text,
            BorderStyle = BorderStyle.FixedSingle
        };
        _txtName.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) AddName(); };
        gbTarget.Controls.Add(_txtName);

        _btnAdd = Btn("+", 394, 42, 44, Color.FromArgb(0, 160, 80));
        _btnAdd.Click += (_, _) => AddName();
        gbTarget.Controls.Add(_btnAdd);

        _btnRemove = Btn("\u2212", 394, 76, 44, Color.FromArgb(180, 50, 50));
        _btnRemove.Click += (_, _) => RemoveName();
        gbTarget.Controls.Add(_btnRemove);

        Controls.Add(gbTarget);
        y += 208;

        // Bottom row
        _chkAuto = CheckBox("Auto-inject on connect", 16, y, null);
        Controls.Add(_chkAuto);

        _lblWorlds = new Label
        {
            Text = "Worlds: \u2014",
            Location = new Point(200, y), Size = new Size(120, 22),
            ForeColor = _dim, BackColor = Color.Transparent, Font = new Font("Segoe UI", 9),
            TextAlign = ContentAlignment.MiddleLeft
        };
        Controls.Add(_lblWorlds);

        _btnRefresh = Btn("Refresh", 360, y, 60, Color.FromArgb(60, 60, 68));
        _btnRefresh.Click += async (_, _) =>
        {
            _btnRefresh.Enabled = false;
            await System.Threading.Tasks.Task.Run(() => RefreshDevice());
            _btnRefresh.Enabled = true;
        };
        Controls.Add(_btnRefresh);

        _btnApply = Btn("Apply && Inject", 422, y, 74, _accent);
        _btnApply.Click += (_, _) => ApplyInject();
        Controls.Add(_btnApply);

        y += 38;

        _lblStatus = new Label
        {
            Text = "Ready",
            Location = new Point(16, y), Size = new Size(480, 20),
            ForeColor = _dim, BackColor = Color.Transparent, Font = new Font("Segoe UI", 9)
        };
        Controls.Add(_lblStatus);
    }

    private Panel GroupBox(int y, int h, string title)
    {
        var p = new Panel
        {
            Location = new Point(12, y), Size = new Size(480, h),
            BackColor = _panel
        };
        p.Paint += (s, e) =>
        {
            var g = e.Graphics;
            using var pen = new Pen(Color.FromArgb(50, 50, 56));
            g.DrawRectangle(pen, 0, 0, p.Width - 1, p.Height - 1);
            g.DrawString(title, new Font("Segoe UI", 9, FontStyle.Bold),
                new SolidBrush(_dim), new PointF(8, -3));
        };
        return p;
    }

    private CheckBox CheckBox(string text, int x, int y, Panel parent)
    {
        var c = new CheckBox
        {
            Text = text, Location = new Point(x, y), Size = new Size(130, 22),
            ForeColor = _text, BackColor = Color.Transparent
        };
        if (parent != null) parent.Controls.Add(c);
        return c;
    }

    private Button Btn(string text, int x, int y, int w, Color color)
    {
        var b = new Button
        {
            Text = text, Location = new Point(x, y), Size = new Size(w, 28),
            BackColor = color, ForeColor = Color.White,
            Font = new Font("Segoe UI", 9, FontStyle.Bold),
            FlatStyle = FlatStyle.Flat,
            FlatAppearance = { BorderSize = 0 },
            UseVisualStyleBackColor = false,
            Cursor = Cursors.Hand
        };
        return b;
    }

    private void LoadSettings()
    {
        _chkMaster.Checked = _settings.Enabled;
        _chkName.Checked = _settings.HideName;
        _chkAvatar.Checked = _settings.HideAvatar;
        _chkCape.Checked = _settings.HideCape;
        _txtTag.Text = _settings.ObfuscationTag;
        _chkAuto.Checked = _settings.AutoInject;
        _radioAll.Checked = !_settings.HideSpecificOnly;
        _radioSpecific.Checked = _settings.HideSpecificOnly;

        _lstBlocked.Items.Clear();
        foreach (var n in _settings.BlockedNames)
            _lstBlocked.Items.Add(n);

        UpdateEnabled();
        UpdateBlocked();
    }

    private void UpdateEnabled()
    {
        var en = _chkMaster.Checked;
        _chkName.Enabled = en;
        _chkAvatar.Enabled = en;
        _chkCape.Enabled = en;
        _txtTag.Enabled = en;
        _radioAll.Enabled = en;
        _radioSpecific.Enabled = en;
        _btnApply.Enabled = en;
        _chkAuto.Enabled = en;
    }

    private void UpdateBlocked()
    {
        var sp = _radioSpecific.Checked;
        _lstBlocked.Enabled = sp;
        _txtName.Enabled = sp;
        _btnAdd.Enabled = sp;
        _btnRemove.Enabled = sp;
    }

    private void AddName()
    {
        var n = _txtName.Text.Trim();
        if (string.IsNullOrEmpty(n)) return;
        if (!_lstBlocked.Items.Contains(n))
        {
            _lstBlocked.Items.Add(n);
            _settings.BlockedNames.Add(n);
            _settings.Save();
        }
        _txtName.Clear();
        _txtName.Focus();
    }

    private void RemoveName()
    {
        if (_lstBlocked.SelectedItem is string n)
        {
            _lstBlocked.Items.Remove(n);
            _settings.BlockedNames.Remove(n);
            _settings.Save();
        }
    }

    private void RefreshDevice()
    {
        SetStatus("Looking for ADB...");
        _adbPath = AdbHelper.FindAdb();
        if (_adbPath == null)
        {
            SetOffline("ADB not found");
            SetStatus("Install Android SDK platform-tools");
            return;
        }

        _deviceSerial = AdbHelper.GetDeviceSerial(_adbPath);
        if (_deviceSerial == null)
        {
            SetOffline("No device connected");
            SetStatus("Connect via USB debugging");
            return;
        }

        var model = AdbHelper.GetDeviceModel(_adbPath, _deviceSerial) ?? _deviceSerial;
        SetOnline(model, _deviceSerial);
        CountWorlds();

        if (_chkAuto.Checked && _chkMaster.Checked)
            ApplyInject();
    }

    private void SetOnline(string model, string serial)
    {
        UI(() =>
        {
            _statusDot.BackColor = _green;
            _lblDevice.Text = model;
            _lblDevice.ForeColor = _text;
        });
    }

    private void SetOffline(string reason)
    {
        UI(() =>
        {
            _statusDot.BackColor = _red;
            _lblDevice.Text = reason;
            _lblDevice.ForeColor = _dim;
            _lblWorlds.Text = "Worlds: \u2014";
        });
    }

    private void CountWorlds()
    {
        if (_deviceSerial == null || _adbPath == null) return;
        var r = AdbHelper.Shell(_adbPath, _deviceSerial,
            "ls /sdcard/games/com.mojang/MinecraftWorlds/ 2>/dev/null | wc -l");
        int t = 0;
        int.TryParse(r?.Trim(), out t);
        UI(() => _lblWorlds.Text = $"Worlds: {t}");
    }

    private void ApplyInject()
    {
        SaveSettings();
        if (_deviceSerial == null || _adbPath == null)
        {
            SetStatus("No device");
            return;
        }

        SetStatus("Sending update...");
        var ok = AdbHelper.SendLiveUpdate(_adbPath, _deviceSerial,
            _chkMaster.Checked ? _settings.ObfuscationTag : "",
            _radioSpecific.Checked ? _settings.BlockedNames : null);

        SetStatus(ok ? "Injected!" : "Failed \u2014 APK installed? USB debugging on?");
        CountWorlds();
    }

    private void SaveSettings()
    {
        _settings.Enabled = _chkMaster.Checked;
        _settings.HideName = _chkName.Checked;
        _settings.HideAvatar = _chkAvatar.Checked;
        _settings.HideCape = _chkCape.Checked;
        _settings.ObfuscationTag = _txtTag.Text;
        _settings.AutoInject = _chkAuto.Checked;
        _settings.HideSpecificOnly = _radioSpecific.Checked;
        _settings.Save();
    }

    private void SetStatus(string m)
    {
        UI(() => _lblStatus.Text = m);
    }

    private void UI(Action a)
    {
        if (IsHandleCreated && InvokeRequired)
            BeginInvoke(a);
        else if (IsHandleCreated)
            a();
    }
}
