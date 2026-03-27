# RapidClicker

RapidClicker is a compact Windows auto clicker built for background use.

It lives in the system tray, starts with administrator privileges, stays sharp on high-DPI displays, and turns a rapid left-click burst into sustained auto-clicking while you keep holding the button.

The standalone native build is also extremely small: the current release executable is under 1 MB, so it is easy to download, keep around, and launch without an extra runtime.

[中文文档](README_ZH.md)

## Screenshot

![image-20250521111327437](./screenshot/tray.png)

**Tray**

![image-20250521111403943](./screenshot/settings.png)

**Settings**

## Features

- Native Win32 executable with a standalone package under 1 MB
- Intelligent click detection for trigger-and-hold auto-clicking
- System tray integration for always-on background use
- Administrator launch for better compatibility with elevated windows
- High-DPI aware interface with English and Chinese support

## How It Works

1. When you click your mouse quickly (default: 5 times within 300ms), the tool enters "rapid click mode"
2. After entering this mode, as long as you hold down the left mouse button, RapidClicker will automatically click at the specified interval
3. When you release the mouse button, automatic clicking stops

## Usage Scenarios

- Games that require rapid clicking
- Applications where repeated clicking is needed
- Testing UI responsiveness
- Any scenario where you want to avoid repetitive strain injury from clicking

## Installation

### Standalone Executable

1. Go to the [Releases page](https://github.com/yanstu/RapidClicker/releases)
2. Download `RapidClicker.exe`
3. Run the executable

## Configuration

Right-click the tray icon and select "Settings" to configure:

- **Trigger Click Count**: How many clicks are needed to enter rapid click mode (default: 5)
- **Trigger Time Window**: Maximum time window (in milliseconds) for trigger clicks (default: 300ms)
- **Auto Click Interval**: Time interval between automatic clicks (in milliseconds) (default: 500ms)
- **Language**: Choose between English and Chinese
- **Auto Start**: Launch through a highest-privilege scheduled task after Windows sign-in

## Building from Source

### Native Build (Default)

Prerequisites:

- Visual Studio Community / Build Tools with Desktop development with C++

Steps:

1. Run:
   ```
   build.bat
   ```
2. Find the native application in:
   ```
   dist\RapidClicker.exe
   ```

### Python Build (Legacy Fallback)

Prerequisites:

- Python 3.7 or higher
- Required packages: see `requirements.txt`

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yanstu/RapidClicker.git
   cd RapidClicker
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the legacy Python build script:
   ```
   build-python.bat
   ```

4. Find the built Python package in the `dist` directory

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Created by [yanstu](https://github.com/yanstu)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
