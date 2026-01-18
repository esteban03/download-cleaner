# Download Cleaner

This is a personal project I whipped up to keep my fucking download folder organized for once.

It is specifically tailored for my Mac setup and isn't intended for widespread distribution as a polished package. I'm sharing the code in a raw, custom way. If it helps you solve a similar problem or inspires your own automation tools, that's great!

## Technologies

*   **Python 3.14+**
*   **[uv](https://github.com/astral-sh/uv)**: An extremely fast Python package installer and resolver.
*   **[Watchdog](https://python-watchdog.readthedocs.io/)**: A library to monitor filesystem events. It is extremely efficient as it leverages native OS events to track folder changes in real-time, avoiding the overhead of constant polling.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd download-cleaner
    ```

2.  **Install dependencies using `uv`:**
    Ensure you have `uv` installed. If not, install it (e.g., `brew install uv`).
    ```bash
    uv sync
    ```

3.  **Configuration:**
    Open `main.py` and ensure the `path` variable points to your Downloads directory:
    ```python
    path = "/Users/YOUR_USERNAME/Downloads"
    ```

## Run as a Service (macOS)

You can set this up as a background service using `launchd` so it runs automatically when you log in.

### 1. Create the Launch Agent

Create a file named `com.user.downloadcleaner.plist` in `~/Library/LaunchAgents/`.

```bash
touch ~/Library/LaunchAgents/com.user.downloadcleaner.plist
```

### 2. Configure the Service

Paste the following configuration into the file. **Important:** Replace `YOUR_USERNAME` and `/PATH/TO/PROJECT` with your actual system values.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.downloadcleaner</string>

    <key>ProgramArguments</key>
    <array>
        <!-- Path to uv executable -->
        <string>/Users/YOUR_USERNAME/.local/bin/uv</string>
        <string>run</string>
        <!-- Absolute path to main.py -->
        <string>/PATH/TO/PROJECT/download-cleaner/main.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/com.user.downloadcleaner.stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/com.user.downloadcleaner.stderr.log</string>

    <key>WorkingDirectory</key>
    <string>/PATH/TO/PROJECT/download-cleaner</string>
</dict>
</plist>
```

### 3. Load and Start the Service

Register the service with `launchctl`:

```bash
launchctl load ~/Library/LaunchAgents/com.user.downloadcleaner.plist
```

To stop or unload the service:

```bash
launchctl unload ~/Library/LaunchAgents/com.user.downloadcleaner.plist
```

### 4. Monitoring

You can check the logs to see if it's working:

```bash
tail -f /tmp/com.user.downloadcleaner.stdout.log
```
