# GlucoClock

A real-time continuous glucose monitoring display with digital clock, designed for Raspberry Pi and desktop use. Perfect for bedside monitoring with automatic alarms for out-of-range glucose levels.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Raspberry%20Pi-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🌟 Features

### Real-time Glucose Monitoring
- **Live glucose readings** from Dexcom CGM devices via Dexcom Share
- **Visual glucose indicator** with color-coded circle:
  - 🔴 Red: < 3.5 mmol/L (low)
  - 🟢 Green: 3.5-10.0 mmol/L (normal)
  - 🟠 Orange: ≥ 10.0 mmol/L (high)
- **Trend arrows** showing glucose direction and rate of change
- **Automatic updates** every 5 minutes
- **Time since last reading** display

### Smart Alarm System
- **Nighttime alarms** (22:30 - 07:00) for out-of-range glucose
- **Distinct audio alerts**:
  - Low glucose (≤ 3.5 mmol/L): Deep 200Hz tone
  - High glucose (≥ 10.0 mmol/L): High 850Hz tone
- **Mute function** with 1-hour countdown timer
- **Test buttons** for alarm sounds

### Digital Clock Display
- **Large, readable time** in 24-hour format
- **Fullscreen mode** for bedside use
- **Dark theme** optimized for nighttime viewing

## 📸 Screenshots

The application features a clean, minimalist interface with:
- Central glucose display with trend arrow
- Digital clock at the bottom
- Control buttons for testing alarms, manual updates, muting, and exit

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Dexcom Share account with CGM data
- GUI support (for desktop/Raspberry Pi with display)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/webdktid/glucose-clock.git
cd glucose-clock
```

2. Install dependencies:
```bash
pip install -r src/requirements.txt
```

3. Configure Dexcom credentials in `src/settings.py`:
```python
DEXCOM_CONFIG = {
    'username': "your_username",
    'password': "your_password",
    'region': "ous"  # or "us" for US users
}
```

### Running the Application

```bash
# Windows
python src/GlucoClock.py

# Linux/Raspberry Pi
python3 src/GlucoClock.py
```

### Keyboard Shortcuts
- `ESC` or `F11`: Toggle fullscreen mode

## 🔧 Configuration

All settings can be customized in `src/settings.py`:

### Glucose Thresholds
```python
LOW_GLUCOSE_THRESHOLD = 3.5   # mmol/L
HIGH_GLUCOSE_THRESHOLD = 10.0  # mmol/L
```

### Alarm Settings
```python
ALARM_START_TIME = 22 * 60 + 30  # 22:30
ALARM_END_TIME = 7 * 60           # 07:00
ALARM_INTERVAL = 120              # seconds between alarms
```

### Display Settings
```python
WINDOW_SIZE = "800x480"  # Optimized for Raspberry Pi touchscreen
UPDATE_INTERVAL = 300    # seconds between glucose updates
```

## 🖥️ Platform-Specific Setup

### Raspberry Pi

Perfect for dedicated bedside monitoring:

1. Enable automatic startup:
```bash
# Add to /etc/xdg/lxsession/LXDE-pi/autostart
@python3 /home/pi/glucose-clock/src/GlucoClock.py
```

2. For touchscreen displays:
- The 800x480 resolution is optimized for official Raspberry Pi touchscreen
- Fullscreen mode removes window decorations

### Windows

Run directly or create a batch file for easy launching:
```batch
@echo off
cd /d "C:\path\to\glucose-clock"
python src\GlucoClock.py
```

## 📦 Dependencies

- **[pydexcom](https://github.com/gagebenne/pydexcom)** - Dexcom Share API integration
- **pygame** - Cross-platform audio playback
- **numpy** - Audio tone generation
- **tkinter** - GUI framework (included with Python)

## 🛡️ Security Notes

- Store Dexcom credentials securely (consider environment variables)
- The application only reads glucose data, never writes
- No data is stored locally or transmitted to third parties

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is not a medical device and should not be used as the primary method for glucose monitoring. Always use official Dexcom applications and devices for medical decisions. This tool is intended as a supplementary display only.

## 🙏 Acknowledgments

- Dexcom for providing the Share API
- The pydexcom library maintainers
- The open-source community

## 📧 Support

For issues, questions, or suggestions, please [open an issue](https://github.com/webdktid/glucose-clock/issues) on GitHub.
