import shutil
import time
import getpass
import subprocess
import typer

from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent

from anxiety.should_be_deleted import ShouldBeDeleted


app = typer.Typer()

command_name = "anxiety"
plist_file_name = "me.steban.www.anxiety.plist"

@app.command()
def watch():
    """
    Watch your Downloads folder for new files.
    """
    downloads_folder = Path("~/Downloads").expanduser()
    target_folder_name = "should-be-deleted"

    class MyHandler(FileSystemEventHandler):
        def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
            print("New file created: ", event.src_path)

            time.sleep(0.5)

            should_be_deleted = ShouldBeDeleted(src_path=event.src_path)
            should_be_deleted.run()

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
    """
    Run anxiety in the background.
    """
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
    """
    Stop the background process.
    """
    result = subprocess.run(
        ["launchctl", "unload", str(_get_target_plist_file_path())],
        capture_output=True,
        text=True
    )

    result.check_returncode()

    typer.secho("Stopped successfully!", fg="green")


@app.command()
def status():
    """
    Check if anxiety is running.
    """
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
        else:
            raise e


if __name__ == "__main__":
    app()