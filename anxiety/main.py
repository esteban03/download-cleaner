import random
import shutil
import time
import getpass
import subprocess
import typer


from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent


app = typer.Typer()

command_name = "anxiety"
plist_file_name = "me.steban.www.anxiety.plist"

@app.command()
def watch():
    downloads_folder = Path("~/Downloads").expanduser()
    target_folder_name = "should-be-deleted"

    class MyHandler(FileSystemEventHandler):
        def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
            print("New file created: ", event.src_path)

            time.sleep(0.5)

            # macos .app files are actually directories (bundles), so recursive monitoring
            # is required to detect their creation. However, this triggers events for every
            # single file inside the bundle.
            # I filter these out by ensuring the event comes directly from the root
            # of the Downloads folder, ignoring nested paths.
            src_path = Path(event.src_path)
            if src_path.parent.name != downloads_folder.name:
                print("Folder skipped: ", event.src_path)
                return

            should_be_deleted: list[Path] = []

            for file in downloads_folder.glob("*.[app,dmg]"):
                if file.suffix in (".app", ".dmg"):
                    should_be_deleted.append(file)

            should_be_deleted_folder = Path(f"{downloads_folder}/{target_folder_name}")
            should_be_deleted_folder.mkdir(exist_ok=True)

            for file in should_be_deleted:
                target = str(should_be_deleted_folder) + "/" + file.name

                if Path(target).exists():
                    random_num = random.randint(1, 1000)
                    target = f"{should_be_deleted_folder}/{file.stem} {random_num}{file.suffix}"

                if file.exists():
                    shutil.move(str(file), target)

                print("Target position: " + target)

            print(f"{len(should_be_deleted)} files should be deleted")

    observer = Observer()
    observer.schedule(MyHandler(), downloads_folder, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()

def _get_target_plist_file_path() -> Path:
    return  Path(f"~/Library/LaunchAgents/{plist_file_name}").expanduser()

@app.command()
def init():
    root_path = Path(__file__).parent

    with open(root_path / "plist.xml", "r") as f:
        plist_content = f.read().format(
            username=getpass.getuser(),
            command_path=shutil.which(command_name),
        )

    plist_file =_get_target_plist_file_path()
    plist_file.parent.mkdir(parents=True, exist_ok=True)
    plist_file.write_text(plist_content)

    result = subprocess.run(
        ["launchctl", "load", str(plist_file)],
        check=True,
        capture_output=True,
        text=True
    )

    result.check_returncode()

    typer.secho("Initialized successfully!", fg="green")


@app.command()
def stop():
    result = subprocess.run(
        ["launchctl", "unload", str(_get_target_plist_file_path())],
        capture_output=True,
        text=True
    )

    result.check_returncode()

    typer.secho("Stopped successfully!", fg="green")


@app.command()
def status():
    process_name = plist_file_name.replace(".plist", "")

    result = subprocess.run(
        ["launchctl", "list", process_name],
        capture_output=True,
        text=True
    )

    try:
        result.check_returncode()
        typer.secho("Service is running", fg="green")
    except subprocess.CalledProcessError as e:
        if e.returncode == 113:
            typer.secho("Services is not running!", fg="red")


if __name__ == "__main__":
    app()