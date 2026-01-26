> 🚧 **Note:** This project is still under development.

# Hacking my Digital Hoarding, one file at a time

This is a personal project I whipped up to keep my fucking download folder organized for once. It is specifically tailored for my Mac setup and isn't intended for widespread distribution as a polished package. I'm sharing the code in a raw, custom way. If it helps you solve a similar problem or inspires your own automation tools, that's great!

I tend to hoard files, installers, and documents with the false promise that *"they will be useful in the future."* Surprise: they never are. The result is a massive cognitive load that affects both my productivity and my Mac's storage.

This project is born from my own **"Mental Framework"** to hack digital hoarding:

1. **Identify the trash:** Recognizing single-use files (currently focusing on installers like `.dmg` or `.app`).
2. **Reduce detachment friction:** Instead of deleting them immediately (which triggers that *"what if I need it later?"* anxiety), I move them to a transition zone.
3. **Automate the habit:** I've realized that the cognitive cost and psychological resistance to deleting things are too high for me. I've accepted it. So, I prefer this script to act as my "organized self" and do the job for me automatically.


<img width="2752" height="1536" alt="fucking-folder" src="https://github.com/user-attachments/assets/6161fb7b-aedf-48b2-8b62-6402e8da4df3" />



## 🚀 The Solution: Version 1.0

This is the first iteration of my cleaning assistant. It uses a **Watchdog** (filesystem observer) to monitor the downloads folder in real-time and apply my framework rules.

### How it works:

- **Auto-Detection:** The script watches for any new item arriving in the folder.
- **Smart Filter:** It processes ALL files in Downloads (except temporary files and the transition folder itself).
- **Move, Don't Delete:** Files are moved to a `should-be-deleted` folder. This hacks the fear of loss, giving me a "grace period" before the final purge.
- **Duplicate Handling:** If I download the same installer multiple times, the script detects name collisions and assigns a random number to avoid errors and keep everything traceable.

## 📋 File Movement & Deletion Rules

The script follows a two-stage approach based on file metadata (`st_ctime` - creation time):

### Stage 1: Movement to Transition Zone
- **Waiting Period:** Files must remain in Downloads for at least **24 hours** before being moved
- **Target Files:** ALL files in Downloads (excluding temporary files and the transition folder)
- **Destination:** `~/Downloads/should-be-deleted/` folder
- **⚠️ macOS Behavior:** When files are moved, macOS treats this as creating a new file, so the creation timestamp (`st_ctime`) resets to the move time

### Stage 2: Automatic Deletion
- **Grace Period:** Files in the transition zone are kept for **1 week** before deletion
- **Timing Logic:** Due to the macOS timestamp reset, the actual deletion occurs 1 week after the file was moved (not 1 week after original download)
- **Example Timeline:**
  - Day 0: File downloaded to Downloads
  - Day 1+: File moved to `should-be-deleted` (timestamp resets)
  - Day 8+: File automatically deleted

### Temporary File Protection
The script skips files matching these patterns to avoid interfering with active downloads:
- `.com.google.Chrome` (Chrome temporary downloads)
- `.tmp`, `.partial`, `.crdownload` (partial downloads)
- `~$` (Office temporary files)

## 🛠️ Technologies

- **Python 3.14+**
- [**uv**](https://github.com/astral-sh/uv): An extremely fast Python package installer and resolver.
- [**Typer**](https://typer.tiangolo.com/): A library for building CLI applications.
- [**Watchdog**](https://python-watchdog.readthedocs.io/): A library to monitor filesystem events. It leverages native OS events to track folder changes in real-time, avoiding the overhead of constant polling.

## 📦 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd anxiety
```

### 2. Install dependencies using `uv`

```bash
uv sync
```

## 🚀 Usage

`anxiety` is now a CLI powered by Typer. You can run it using `uv run anxiety`.

### Monitor Downloads (Foreground)
To start watching your Downloads folder in real-time immediately:
```bash
uv run anxiety watch
```

### Background Service (Daemon)
You can run the cleaner as a background service that starts automatically when you log in.

**Start & Enable:**
```bash
uv run anxiety init
```
This command automatically:
1. Generates the Launch Agent configuration.
2. Installs it to `~/Library/LaunchAgents/me.steban.www.anxiety.plist`.
3. **Starts the service immediately.**

**Stop & Disable:**
```bash
uv run anxiety stop
```
This stops the background service and unloads it from the system.

### Logs
To verify the service is working or debug issues, check the logs:
```bash
tail -f /tmp/me.steban.www.anxiety.stdout.log
```

## 🔮 Next Steps

- [x] **Auto-Purge:** Implement auto-deletion rules for the `should-be-deleted` folder (e.g., delete files older than 30 days).
- [ ] **PyPI Publication:** Package `anxiety` for easy installation via `pip install anxiety`.
- [ ] **Homebrew Support:** Create a formula to install via `brew install anxiety`.
- [ ] **Desktop Zen Mode:** Auto-organize the Mac Desktop to keep it always pristine, highlighting the wallpaper and reducing visual noise.
