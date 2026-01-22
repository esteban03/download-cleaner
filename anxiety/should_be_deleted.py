import random
import shutil
from datetime import timedelta, datetime
from pathlib import Path


class Rules:
    # less than 1 day is too new to move inside should_be_delete folder
    is_too_new = timedelta(days=1)

    max_time_before_to_delete = timedelta(weeks=1)

    # Files that are currently being downloaded (temporary files)
    temporary_patterns = {
        ".com.google.Chrome",  # Chrome temporary downloads
        ".tmp",  # Generic temp files
        ".partial",  # Partial downloads
        "~$",  # Office temporary files
        ".crdownload",
    }


class ShouldBeDeleted:
    _downloads_folder: Path
    _should_be_deleted_folder: Path
    _target_folder_name = "should-be-deleted"

    def __init__(self, src_path: str) -> None:
        self.path = Path(src_path)
        self._downloads_folder = Path("~/Downloads").expanduser()
        self._should_be_deleted_folder = self._downloads_folder / self._target_folder_name

    def _detect_files(self) -> list[Path]:
        files: list[Path] = [
            file
            for file in self._downloads_folder.iterdir()
            if not self._skipped(file)
        ]
        return files

    def _skipped(self, file: Path) -> bool:
        # skip the target folder
        if self._target_folder_name in file.name:
            return True

        # check if the file it's a temporary file used for a process like chrome download
        if any(pattern in file.name for pattern in Rules.temporary_patterns):
            print("Temporary file or folder skipped -> " + file.name)
            return True

        creation_date = datetime.fromtimestamp(file.stat().st_ctime)
        if (datetime.now() - creation_date) < Rules.is_too_new:
            print(f"Too new file [{creation_date}] [{datetime.now() - creation_date}] -> " + file.name)
            return True

        return False

    def _move_files(self) -> None:
        self._should_be_deleted_folder.mkdir(parents=True, exist_ok=True)

        should_be_deleted = self._detect_files()

        for file in should_be_deleted:

            target_folder_path = self._should_be_deleted_folder / file.name

            if target_folder_path.exists():
                random_num = random.randint(1, 1000)
                target_folder_path = f"{target_folder_path.stem} {random_num}{file.suffix}"

            if file.exists():
                shutil.move(str(file), target_folder_path)

            print(f"Target position: {target_folder_path}")

    def run(self) -> None:
        # macos .app files are actually directories (bundles), so recursive monitoring
        # is required to detect their creation. However, this triggers events for every
        # single file inside the bundle.
        # I filter these out by ensuring the event comes directly from the root
        # of the Downloads folder, ignoring nested paths.
        if self.path.parent.name != self._downloads_folder.name:
            return


        print("Running...")
        self._move_files()
        self._delete_files()
        print("Done!")

    def _delete(self, file: Path) -> None:
        if file.is_dir():
            shutil.rmtree(str(file.parent))
            return

        file.unlink()

    def _delete_files(self) -> None:
        if not self._should_be_deleted_folder.exists():
            return

        print("Deleting files...")

        files = self._should_be_deleted_folder.iterdir()

        for file in files:
            created_date = datetime.fromtimestamp(file.stat().st_ctime)

            if (datetime.now() - created_date) < Rules.max_time_before_to_delete:
                print(f"Too new to delete [{created_date}] [{datetime.now() - created_date}] -> {file.name}")
                continue

            self._delete(file)

            print(f"Deleted file: {file.name}")
