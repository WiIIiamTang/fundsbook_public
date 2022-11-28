import requests
import os

from .constants import BASE_PATH


class Updater:
    def __init__(self, url):
        self.url = url
        self.version = None
        self.download_url = None

    def check(self):
        try:
            r = requests.get(self.url)
            if r.status_code == 200:
                self.version = r.json()["version"]
                self.download_url = r.json()["download_url"]
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def download(self):
        try:
            r = requests.get(self.download_url)
            if r.status_code == 200:
                with open(os.path.join(BASE_PATH, "update.zip"), "wb") as f:
                    f.write(r.content)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
