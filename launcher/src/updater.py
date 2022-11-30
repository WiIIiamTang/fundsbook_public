import requests
import subprocess
import os
import traceback
import stat
import pathlib
import zipfile
import shutil
from packaging import version

from .constants import BASE_PATH, PROD, LAUNCHER_INTERNAL_VERSION, APP_INTERNAL_VERSION


class Updater:
    def __init__(self, url):
        self.repo_url = url
        self.repo_version = None
        self.app_version = APP_INTERNAL_VERSION
        self.local_version = LAUNCHER_INTERNAL_VERSION
        self.download_url = None
        self.new_app_update = False
        self.new_lu_update = False
        print(self)

    def __str__(self):
        return f"Local launcher version: {self.local_version} | Local app version: {self.app_version}"

    def check(self):
        try:
            with open(os.path.join(BASE_PATH, "VERSION")) as f:
                self.local_version = f.read().strip()
            with open(
                os.path.join(os.path.join(BASE_PATH, ".."), "app", "VERSION"), "r"
            ) as f:
                self.app_version = f.read().strip()
            print(f"Checking for launcher update at {self.repo_url}")
            r = requests.get(self.repo_url)
            if r.status_code == 200:
                self.repo_version = r.json()["tag_name"]
                self.download_url = r.json()["assets"][0]["browser_download_url"]
                print(f"Latest launcher version: {self.repo_version}")
                self.repo_lu_version = self.repo_version.split("+")[1].split("--")[1]
                self.repo_app_version = self.repo_version.split("+")[0].strip("v")
                self.new_app_update = version.parse(
                    self.repo_app_version
                ) > version.parse(self.app_version)
                self.new_lu_update = version.parse(
                    self.repo_lu_version
                ) > version.parse(self.local_version)

                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def download(self, cleanup_downloads=False):
        if self.new_app_update:
            if not PROD:
                print("Not in bundled app, skipping download")
                return False
            try:
                r = requests.get(self.download_url)
                if r.status_code == 200:
                    print("Downloading...")
                    with open(
                        os.path.join(os.path.join(BASE_PATH, ".."), "update.zip"), "wb"
                    ) as f:
                        f.write(r.content)
                    print("Download complete.")

                    return self.update_files(cleanup_downloads=cleanup_downloads)
                else:
                    print("Download failed.")
                    return False
            except Exception as e:
                print(e)
                return False
        else:
            print("No update available.")
            return False

    def update_files(self, cleanup_downloads=False):
        if not PROD:
            print("Not in bundled app, skipping update")
            return False
        try:
            # rename the old app folder
            parent = pathlib.Path(BASE_PATH).parent.absolute()
            os.rename(
                os.path.join(parent, "app"),
                os.path.join(parent, "old-app"),
            )
            # os.mkdir("app")

            # extract the new launcher folder
            os.mkdir("tmp")
            with zipfile.ZipFile(os.path.join(parent, "update.zip"), "r") as zip_ref:
                zip_ref.extractall(path=os.path.join(parent, "tmp"))

            # move the new launcher folder to the root
            shutil.move(
                os.path.join(parent, "tmp", "app"),
                os.path.join(parent),
            )

            # cleanup
            def remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                print("trying to remove again")
                func(path)

            print("Cleaning up...")
            if cleanup_downloads:
                print("cleaning up fundbook_release folder")
                shutil.rmtree(os.path.join(parent, "tmp"), onerror=remove_readonly)
            shutil.rmtree(os.path.join(parent, "old-app"), onerror=remove_readonly)
            os.remove(os.path.join(parent, "update.zip"))

            return True
        except Exception as e:
            print("error while updating files.")
            print(e)
            print(traceback.format_exc())
            return False

    def install_update(self):
        if self.new_lu_update and not self.new_app_update:
            print("Installing launcher update")
            if PROD:
                subprocess.Popen(
                    [
                        os.path.join(
                            os.path.join(BASE_PATH, ".."), "launcher-updater.exe"
                        ),
                        self.local_version,
                        os.path.join(BASE_PATH, ".."),
                        "--cleanup_downloads",
                    ]
                )
                self.close()
            else:
                subprocess.Popen(
                    [
                        "python",
                        os.path.join(
                            os.path.join(BASE_PATH, ".."),
                            "launcher-updater",
                            "launcher-updater.py",
                        ),
                        self.local_version,
                        os.path.join(BASE_PATH, ".."),
                        "--cleanup_downloads",
                    ]
                )
        elif self.new_app_update and not self.new_lu_update:
            print("Installing app update")
            if PROD:
                self.download(cleanup_downloads=True)
        elif self.new_app_update and self.new_lu_update:
            print("Installing app and launcher update")
            if PROD:
                self.download(cleanup_downloads=False)
                subprocess.Popen(
                    [
                        os.path.join(
                            os.path.join(BASE_PATH, ".."), "launcher-updater.exe"
                        ),
                        self.local_version,
                        os.path.join(BASE_PATH, ".."),
                        "--cleanup-downloads",
                        "--use_cached",
                    ]
                )
                self.close()
            else:
                self.download()
                self.update_files(cleanup_downloads=False)
                subprocess.Popen(
                    [
                        "python",
                        os.path.join(
                            os.path.join(BASE_PATH, ".."),
                            "launcher-updater",
                            "launcher-updater.py",
                        ),
                        self.local_version,
                        os.path.join(BASE_PATH, ".."),
                        "--cleanup-downloads",
                        "--use_cached",
                    ]
                )

        return "Done"
