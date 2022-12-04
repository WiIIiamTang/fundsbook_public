import requests
import os
import zipfile
import stat
import shutil
from packaging import version

from .constants import PROD, BASE_PATH


class Updater:
    def __init__(
        self, url, local_version, base_path, cleanup_downloads, use_cached=False
    ):
        self.repo_url = url
        self.repo_version = None
        self.local_version = local_version
        self.download_url = None
        self.new_lu_update = False
        self.BASE_PATH = base_path
        self.cleanup_downloads = cleanup_downloads
        self.use_cached = use_cached
        print(self)

    def __str__(self):
        return f"Local launcher version: {self.local_version}"

    def check(self):
        try:
            print(f"Checking for launcher update at {self.repo_url}")
            r = requests.get(self.repo_url)
            if r.status_code == 200:
                self.repo_version = r.json()["tag_name"]
                self.download_url = r.json()["assets"][0]["browser_download_url"]
                print(f"Latest launcher version: {self.repo_version}")
                self.repo_lu_version = self.repo_version.split("+")[1].split("--")[1]
                self.new_lu_update = version.parse(
                    self.repo_lu_version
                ) > version.parse(self.local_version)
                print(self.BASE_PATH)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def download(self):
        if self.new_lu_update:
            if not PROD:
                print("Not in bundled app, skipping download")
                return False
            try:
                if not self.use_cached:
                    r = requests.get(self.download_url)
                    if r.status_code == 200:
                        print("Downloading...")
                        with open(
                            os.path.join(self.BASE_PATH, "update.zip"), "wb"
                        ) as f:
                            f.write(r.content)
                        print("Download complete.")

                    return self.update_files()
                else:
                    print("Download failed.")
                    return False
            except Exception as e:
                print(e)
                return False
        else:
            print("No update available.")
            return False

    def update_files(self):
        if not PROD:
            print("Not in bundled app, skipping update")
            return False
        try:
            print("Updating files...")
            # rename the old launcher folder
            os.rename(
                os.path.join(self.BASE_PATH, "launcher"),
                os.path.join(self.BASE_PATH, "old-launcher"),
            )

            os.mkdir("tmp")
            # extract the new launcher folder
            if not self.use_cached:
                with zipfile.ZipFile(
                    os.path.join(self.BASE_PATH, "update.zip"), "r"
                ) as zip_ref:
                    for file in zip_ref.namelist():
                        zip_ref.extract(file, os.path.join(self.BASE_PATH, "tmp"))

            # move the new launcher folder to the root
            shutil.move(
                os.path.join(self.BASE_PATH, "tmp", "launcher"),
                os.path.join(self.BASE_PATH, "launcher"),
            )

            # cleanup
            def remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                print("trying to remove again")
                func(path)

            if self.cleanup_downloads:
                shutil.rmtree(
                    os.path.join(self.BASE_PATH, "tmp"),
                    onerror=remove_readonly,
                )
            if not self.use_cached:
                shutil.rmtree(
                    os.path.join(self.BASE_PATH, "old-launcher"),
                    onerror=remove_readonly,
                )
                os.remove(os.path.join(self.BASE_PATH, "update.zip"))

            return True
        except Exception as e:
            return False
