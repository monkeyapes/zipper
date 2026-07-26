using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace LocalNameControl;

public class MainForm : Form
{
    private AppSettings _settings;
    private string _adbPath;
    private string _deviceSerial;

    // Device panel
    private Panel _devicePanel;
    private Label _lblDeviceIcon;
    private Label _lblDeviceTitle;
    private Label _lblDeviceModel;
    private Label _lblDeviceSerial;
    private Panel _statusDot;

    // Main toggle
    private Panel _togglePanel;
    private Label _lblToggle;
    private Panel _toggleSwitch;
    private bool _toggleOn;

    // Checkboxes
    private CheckBox _chkHideName;
    private CheckBox _chkHideAvatar;
    private CheckBox _chkHideCape;

    // Tag input
    private TextBox _txtTag;

    // Mode + blocked names
    private RadioButton _radioHideAll;
    private RadioButton _radioHideSpecific;
    private ListBox _lstBlocked;
    private TextBox _txtNewName;
    private Button _btnAdd;
    private Button _btnRemove;

    // Bottom bar
    private CheckBox _chkAutoInject;
    private Label _lblWorldStatus;
    private Button _btnRefresh;
    private Button _btnApply;
    private Label _lblStatus;

    // Colors
    private readonly Color _bg = Color.FromArgb(18, 18, 22);
    private readonly Color _panelBg = Color.FromArgb(28, 28, 34);
    private readonly Color _accent = Color.FromArgb(0, 140, 255);
    private readonly Color _accentDim = Color.FromArgb(0, 120, 220);
    private readonly Color _text = Color.FromArgb(220, 220, 225);
    private readonly Color _textDim = Color.FromArgb(130, 130, 140);
    private readonly Color _border = Color.FromArgb(50, 50, 58);
    private readonly Color _green = Color.FromArgb(0, 200, 100);
    private readonly Color _red = Color.FromArgb(220, 60, 60);

    public MainForm()
    {
        _settings = AppSettings.Load();
        InitializeComponent();
        LoadSettings();
        BeginInvoke(() => RefreshDevice());
    }

    private void InitializeComponent()
    {
        Text = "LocalName";
        Size = new Size(540, 600);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        BackColor = _bg;
        ForeColor = _text;
        Font = new Font("Segoe UI", 10);
        DoubleBuffered = true;

        // ── DEVICE PANEL ──
        _devicePanel = new Panel
        {
            Location = new Point(12, 12),
            Size = new Size(504, 80),
            BackColor = _panelBg
        };
        _devicePanel.Paint += (s, e) =>
        {
            var g = e.Graphics;
            using var pen = new Pen(_border);
            g.DrawRectangle(pen, 0, 0, _devicePanel.Width - 1, _devicePanel.Height - 1);
        };
        Controls.Add(_devicePanel);

        _statusDot = new Panel
        {
            Location = new Point(16, 14),
            Size = new Size(12, 12),
            BackColor = _red
        };
        _devicePanel.Controls.Add(_statusDot);

        _lblDeviceIcon = new Label
        {
            Text = "\U0001F4F1",
            Location = new Point(14, 34),
            Size = new Size(28, 28),
            Font = new Font("Segoe UI", 16),
            ForeColor = _text,
            BackColor = Color.Transparent
        };
        _devicePanel.Controls.Add(_lblDeviceIcon);

        _lblDeviceTitle = new Label
        {
            Text = "No device",
            Location = new Point(50, 12),
            Size = new Size(200, 22),
            Font = new Font("Segoe UI", 11, FontStyle.Bold),
            ForeColor = _text,
            BackColor = Color.Transparent
        };
        _devicePanel.Controls.Add(_lblDeviceTitle);

        _lblDeviceModel = new Label
        {
            Text = "Disconnected",
            Location = new Point(50, 34),
            Size = new Size(200, 18),
            Font = new Font("Segoe UI", 9),
            ForeColor = _textDim,
            BackColor = Color.Transparent
        };
        _devicePanel.Controls.Add(_lblDeviceModel);

        _lblDeviceSerial = new Label
        {
            Text = "",
            Location = new Point(50, 52),
            Size = new Size(200, 18),
            Font = new Font("Segoe UI", 9),
            ForeColor = _textDim,
            BackColor = Color.Transparent
        };
        _devicePanel.Controls.Add(_lblDeviceSerial);

        // ── TOGGLE ──
        _togglePanel = new Panel
        {
            Location = new Point(12, 100),
            Size = new Size(504, 52),
            BackColor = _panelBg
        };
        _togglePanel.Paint += (s, e) =>
        {
            using var pen = new Pen(_border);
            e.Graphics.DrawRectangle(pen, 0, 0, _togglePanel.Width - 1, _togglePanel.Height - 1);
        };
        Controls.Add(_togglePanel);

        _lblToggle = new Label
        {
            Text = "Master Toggle",
            Location = new Point(16, 14),
            Size = new Size(120, 24),
            Font = new Font("Segoe UI", 11, FontStyle.Bold),
            ForeColor = _text,
            BackColor = Color.Transparent
        };
        _togglePanel.Controls.Add(_lblToggle);

        _toggleSwitch = new Panel
        {
            Location = new Point(440, 13),
            Size = new Size(48, 26),
            BackColor = _red
        };
        _toggleSwitch.MouseClick += (s, e) => { ToggleSwitch(); };
        _toggleSwitch.Paint += (s, e) =>
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            var r = new Rectangle(2, 2, 22, 22);
            using var btn = new SolidBrush(Color.White);
            g.FillEllipse(btn, r);
        };
        _togglePanel.Controls.Add(_toggleSwitch);

        // ── CHECKBOXES ──
        var chkPanel = new Panel
        {
            Location = new Point(12, 160),
            Size = new Size(504, 80),
            BackColor = _panelBg
        };
        chkPanel.Paint += (s, e) =>
        {
            using var pen = new Pen(_border);
            e.Graphics.DrawRectangle(pen, 0, 0, chkPanel.Width - 1, chkPanel.Height - 1);
        };
        Controls.Add(chkPanel);

        _chkHideName = MakeCheckBox("\U0001F464 Hide Name", 16, 12);
        _chkHideAvatar = MakeCheckBox("\U0001F9CD Hide Avatar", 180, 12);
        _chkHideCape = MakeCheckBox("\U0001F9E5 Hide Cape", 344, 12);
        chkPanel.Controls.Add(_chkHideName);
        chkPanel.Controls.Add(_chkHideAvatar);
        chkPanel.Controls.Add(_chkHideCape);

        var lblTag = new Label
        {
            Text = "Obfuscation Tag:",
            Location = new Point(16, 44),
            Size = new Size(120, 22),
            ForeColor = _textDim,
            BackColor = Color.Transparent,
            Font = new Font("Segoe UI", 9)
        };
        chkPanel.Controls.Add(lblTag);

        _txtTag = new TextBox
        {
            Location = new Point(140, 42),
            Size = new Size(348, 24),
            BackColor = Color.FromArgb(38, 38, 44),
            ForeColor = _text,
            BorderStyle = BorderStyle.FixedSingle,
            Text = _settings.ObfuscationTag,
            Font = new Font("Consolas", 10)
        };
        chkPanel.Controls.Add(_txtTag);

        // ── MODE + BLOCKED LIST ──
        var modePanel = new Panel
        {
            Location = new Point(12, 248),
            Size = new Size(504, 220),
            BackColor = _panelBg
        };
        modePanel.Paint += (s, e) =>
        {
            using var pen = new Pen(_border);
            e.Graphics.DrawRectangle(pen, 0, 0, modePanel.Width - 1, modePanel.Height - 1);
        };
        Controls.Add(modePanel);

        var lblMode = new Label
        {
            Text = "Target Mode",
            Location = new Point(16, 12),
            Size = new Size(120, 22),
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            ForeColor = _text,
            BackColor = Color.Transparent
        };
        modePanel.Controls.Add(lblMode);

        _radioHideAll = new RadioButton
        {
            Text = "Hide ALL players",
            Location = new Point(16, 38),
            Size = new Size(150, 22),
            ForeColor = _text,
            BackColor = Color.Transparent,
            FlatStyle = FlatStyle.Flat,
            Checked = !_settings.HideSpecificOnly
        };
        _radioHideAll.CheckedChanged += (_, _) => UpdateBlockedState();
        modePanel.Controls.Add(_radioHideAll);

        _radioHideSpecific = new RadioButton
        {
            Text = "Hide SPECIFIC players",
            Location = new Point(180, 38),
            Size = new Size(180, 22),
            ForeColor = _text,
            BackColor = Color.Transparent,
            FlatStyle = FlatStyle.Flat,
            Checked = _settings.HideSpecificOnly
        };
        _radioHideSpecific.CheckedChanged += (_, _) => UpdateBlockedState();
        modePanel.Controls.Add(_radioHideSpecific);

        var sep = new Panel
        {
            Location = new Point(16, 66),
            Size = new Size(472, 1),
            BackColor = _border
        };
        modePanel.Controls.Add(sep);

        var lblBlocked = new Label
        {
            Text = "Blocked Players",
            Location = new Point(16, 76),
            Size = new Size(120, 22),
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            ForeColor = _text,
            BackColor = Color.Transparent
        };
        modePanel.Controls.Add(lblBlocked);

        _lstBlocked = new ListBox
        {
            Location = new Point(16, 100),
            Size = new Size(340, 140),
            BackColor = Color.FromArgb(38, 38, 44),
            ForeColor = _text,
            BorderStyle = BorderStyle.FixedSingle,
            Font = new Font("Segoe UI", 10),
            IntegralHeight = false,
            Sorted = true
        };
        modePanel.Controls.Add(_lstBlocked);

        _txtNewName = new TextBox
        {
            Location = new Point(368, 100),
            Size = new Size(120, 22),
            BackColor = Color.FromArgb(38, 38, 44),
            ForeColor = _text,
            BorderStyle = BorderStyle.FixedSingle,
            Font = new Font("Segoe UI", 9)
        };
        _txtNewName.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) AddBlockedName(); };
        modePanel.Controls.Add(_txtNewName);

        _btnAdd = new Button
        {
            Text = "+",
            Location = new Point(368, 126),
            Size = new Size(120, 28),
            BackColor = Color.FromArgb(0, 160, 80),
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            FlatAppearance = { BorderSize = 0 },
            Cursor = Cursors.Hand
        };
        _btnAdd.Click += (_, _) => AddBlockedName();
        modePanel.Controls.Add(_btnAdd);

        _btnRemove = new Button
        {
            Text = "\u2212 Remove",
            Location = new Point(368, 160),
            Size = new Size(120, 28),
            BackColor = Color.FromArgb(180, 50, 50),
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Font = new Font("Segoe UI", 9),
            FlatAppearance = { BorderSize = 0 },
            Cursor = Cursors.Hand
        };
        _btnRemove.Click += (_, _) => RemoveBlockedName();
        modePanel.Controls.Add(_btnRemove);

        // ── BOTTOM BAR ──
        _chkAutoInject = new CheckBox
        {
            Text = "Auto-inject on connect",
            Location = new Point(16, 478),
            Size = new Size(170, 22),
            ForeColor = _textDim,
            BackColor = Color.Transparent,
            FlatStyle = FlatStyle.Flat
        };
        Controls.Add(_chkAutoInject);

        _lblWorldStatus = new Label
        {
            Text = "Worlds: \u2014",
            Location = new Point(200, 478),
            Size = new Size(130, 22),
            ForeColor = _textDim,
            BackColor = Color.Transparent,
            Font = new Font("Segoe UI", 9),
            TextAlign = ContentAlignment.MiddleLeft
        };
        Controls.Add(_lblWorldStatus);

        _btnRefresh = MakeButton("\U0001F504 Refresh", 12, 508, 160, _accentDim);
        _btnRefresh.Click += async (_, _) =>
        {
            _btnRefresh.Enabled = false;
            await System.Threading.Tasks.Task.Run(() => RefreshDevice());
            _btnRefresh.Enabled = true;
        };
        Controls.Add(_btnRefresh);

        _btnApply = MakeButton("\u25B6 Apply && Inject", 368, 508, 148, _accent);
        _btnApply.Click += (_, _) => ApplyAndInject();
        Controls.Add(_btnApply);

        _lblStatus = new Label
        {
            Text = "Ready",
            Location = new Point(12, 546),
            Size = new Size(516, 18),
            ForeColor = _textDim,
            BackColor = Color.Transparent,
            Font = new Font("Segoe UI", 9)
        };
        Controls.Add(_lblStatus);
    }

    private CheckBox MakeCheckBox(string text, int x, int y)
    {
        return new CheckBox
        {
            Text = text,
            Location = new Point(x, y),
            Size = new Size(150, 22),
            ForeColor = _text,
            BackColor = Color.Transparent,
            FlatStyle = FlatStyle.Flat,
            FlatAppearance = { CheckedBackColor = _accent }
        };
    }

    private Button MakeButton(string text, int x, int y, int w, Color color)
    {
        var btn = new Button
        {
            Text = text,
            Location = new Point(x, y),
            Size = new Size(w, 32),
            BackColor = color,
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            FlatAppearance = { BorderSize = 0 },
            Cursor = Cursors.Hand
        };
        return btn;
    }

    private void LoadSettings()
    {
        _toggleOn = _settings.Enabled;
        UpdateToggleVisual();
        _chkHideName.Checked = _settings.HideName;
        _chkHideAvatar.Checked = _settings.HideAvatar;
        _chkHideCape.Checked = _settings.HideCape;
        _txtTag.Text = _settings.ObfuscationTag;
        _chkAutoInject.Checked = _settings.AutoInject;
        _radioHideAll.Checked = !_settings.HideSpecificOnly;
        _radioHideSpecific.Checked = _settings.HideSpecificOnly;

        _lstBlocked.Items.Clear();
        foreach (var name in _settings.BlockedNames)
            _lstBlocked.Items.Add(name);

        UpdateBlockedState();
        UpdateEnabledState();
    }

    private void UpdateToggleVisual()
    {
        _toggleSwitch.BackColor = _toggleOn ? _green : _red;
        _toggleSwitch.Invalidate();
    }

    private void ToggleSwitch()
    {
        _toggleOn = !_toggleOn;
        UpdateToggleVisual();
        UpdateEnabledState();
    }

    private void UpdateEnabledState()
    {
        bool en = _toggleOn;
        _chkHideName.Enabled = en;
        _chkHideAvatar.Enabled = en;
        _chkHideCape.Enabled = en;
        _txtTag.Enabled = en;
        _radioHideAll.Enabled = en;
        _radioHideSpecific.Enabled = en;
        _btnApply.Enabled = en;
    }

    private void UpdateBlockedState()
    {
        bool specific = _radioHideSpecific.Checked;
        _lstBlocked.Enabled = specific;
        _txtNewName.Enabled = specific;
        _btnAdd.Enabled = specific;
        _btnRemove.Enabled = specific;
    }

    private void AddBlockedName()
    {
        var name = _txtNewName.Text.Trim();
        if (string.IsNullOrEmpty(name)) return;
        if (!_lstBlocked.Items.Contains(name))
        {
            _lstBlocked.Items.Add(name);
            _settings.BlockedNames.Add(name);
            _settings.Save();
        }
        _txtNewName.Clear();
        _txtNewName.Focus();
        SetStatus($"Added \u201c{name}\u201d to block list");
    }

    private void RemoveBlockedName()
    {
        if (_lstBlocked.SelectedItem is string name)
        {
            _lstBlocked.Items.Remove(name);
            _settings.BlockedNames.Remove(name);
            _settings.Save();
            SetStatus($"Removed \u201c{name}\u201d from block list");
        }
    }

    private void RefreshDevice()
    {
        SetStatus("Looking for ADB...");
        _adbPath = AdbHelper.FindAdb();
        if (_adbPath == null)
        {
            SetDeviceOffline("ADB not found");
            SetStatus("Install Android SDK platform-tools");
            return;
        }

        _deviceSerial = AdbHelper.GetDeviceSerial(_adbPath);
        if (_deviceSerial == null)
        {
            SetDeviceOffline("No device connected");
            SetStatus("Connect an Android device via USB debugging");
            return;
        }

        var model = AdbHelper.GetDeviceModel(_adbPath, _deviceSerial) ?? _deviceSerial;
        SetDeviceOnline(model, _deviceSerial);
        CountWorlds();

        if (_chkAutoInject.Checked && _toggleOn)
            ApplyAndInject();
    }

    private void SetDeviceOnline(string model, string serial)
    {
        Invoke(() =>
        {
            _statusDot.BackColor = _green;
            _lblDeviceTitle.Text = model;
            _lblDeviceModel.Text = "Connected";
            _lblDeviceSerial.Text = serial;
            _lblDeviceTitle.ForeColor = _text;
        });
    }

    private void SetDeviceOffline(string reason)
    {
        Invoke(() =>
        {
            _statusDot.BackColor = _red;
            _lblDeviceTitle.Text = "No device";
            _lblDeviceModel.Text = reason;
            _lblDeviceSerial.Text = "";
            _lblDeviceTitle.ForeColor = _textDim;
            _lblWorldStatus.Text = "Worlds: \u2014";
        });
    }

    private void CountWorlds()
    {
        if (_deviceSerial == null || _adbPath == null) return;
        var result = AdbHelper.Shell(_adbPath, _deviceSerial,
            "ls /sdcard/games/com.mojang/MinecraftWorlds/ 2>/dev/null | wc -l");
        int total = 0;
        int.TryParse(result?.Trim(), out total);
        Invoke(() => _lblWorldStatus.Text = $"Worlds: {total}");
    }

    private void ApplyAndInject()
    {
        SaveSettings();
        if (_deviceSerial == null || _adbPath == null)
        {
            SetStatus("No device connected");
            return;
        }

        SetStatus("Applying and injecting...");

        var sent = AdbHelper.SendLiveUpdate(_adbPath, _deviceSerial,
            _toggleOn ? _settings.ObfuscationTag : "",
            _radioHideSpecific.Checked ? _settings.BlockedNames : null);

        if (sent)
            SetStatus("Live update sent \u2014 injecting into worlds");
        else
            SetStatus("Failed \u2014 is the APK installed and USB debugging on?");

        CountWorlds();
    }

    private void SaveSettings()
    {
        _settings.Enabled = _toggleOn;
        _settings.HideName = _chkHideName.Checked;
        _settings.HideAvatar = _chkHideAvatar.Checked;
        _settings.HideCape = _chkHideCape.Checked;
        _settings.ObfuscationTag = _txtTag.Text;
        _settings.AutoInject = _chkAutoInject.Checked;
        _settings.HideSpecificOnly = _radioHideSpecific.Checked;

        // BlockedNames already updated in Add/Remove methods

        _settings.Save();
    }

    private void SetStatus(string msg)
    {
        if (InvokeRequired)
            Invoke(() => _lblStatus.Text = msg);
        else
            _lblStatus.Text = msg;
    }
}
