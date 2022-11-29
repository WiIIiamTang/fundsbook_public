import logging
import random
import json
import os
import functools
import subprocess
from time import time, sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException

from ..constants import BASE_PATH

# flag = 0x08000000  # No-Window flag
# webdriver.common.service.subprocess.Popen = functools.partial(
#     subprocess.Popen, creationflags=flag
# )


class EastMoneyFundScraper:
    """
    Represents a web scraper that parses certain pages from EastMoneyFund.
    Meant for "Funds" and "Ranking" sheets on the Excel workbook.
    Note that utf-8 encoding should be used when exporting to files due to chinese characters.
    """

    def __init__(
        self,
        driver_options_arguments: list = [],
        page_timeout: int = 30,
        request_pause: int = 15,
        random_pauses: bool = True,
        driver: str = "firefox",
    ):
        self.driver_options_arguments = driver_options_arguments
        self.page_timeout = page_timeout
        self.request_pause = request_pause
        self.random_pauses = random_pauses

        self.base_url_ranking = "http://fundf10.eastmoney.com/jdzf_"
        self.base_url_funds = "http://fundf10.eastmoney.com/jjjz_"
        self.driver = None
        self.data = {"ranking": {}, "funds": {}, "top": []}
        self.updated = False
        self.is_on = False
        self.first = True
        self.funds_page = 1
        self.driver = driver

    def __str__(self) -> str:
        return f"EastMoneyFund parser | data updated: {self.updated}"

    def start_driver(self) -> bool:
        if self.driver == "firefox":
            self.start_firefox_driver()
        elif self.driver == "chrome":
            self.start_chrome_driver()

    def start_firefox_driver(self, driver_path: str = "geckodriver.exe") -> bool:
        try:
            logging.info("[start driver] starting geckodriver")
            options = Options()
            for arg in self.driver_options_arguments:
                logging.debug(f"[start driver] added option to driver: {arg}")
                options.add_argument(arg)

            profile = webdriver.FirefoxProfile()

            profile.set_preference(
                "general.useragent.override",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            )

            self.driver = webdriver.Firefox(
                firefox_profile=profile, options=options, executable_path=driver_path
            )
            self.driver.set_page_load_timeout(self.page_timeout)
            self.is_on = True
        except Exception as e:
            logging.error(e)
            logging.error("[start driver] The selenium driver failed to start.")
            return False
        return True

    def start_chrome_driver(self, driver_path: str = "chromedriver.exe") -> bool:
        try:
            logging.info("[start driver] starting chromedriver")
            options = Options()
            for arg in self.driver_options_arguments:
                logging.debug(f"[start driver] added option to driver: {arg}")
                options.add_argument(arg)

            # options.add_argument("--remote-debugging-port=9222")

            options.binary_location = (
                r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            )
            # options.binary_location = driver_path
            logging.info(driver_path)
            # logging.info(options)
            chrome_service = ChromeService(driver_path)
            chrome_service.creation_flags = subprocess.CREATE_NO_WINDOW
            self.driver = webdriver.Chrome(
                options=options,
                executable_path=os.path.join(BASE_PATH, "drivers", driver_path),
                service=chrome_service,
            )
            self.driver.set_page_load_timeout(self.page_timeout)
            self.is_on = True
        except Exception as e:
            logging.error(e)
            logging.error("[start driver] The selenium driver failed to start.")
            return False
        return True

    def _get_page(
        self, url: str, progress_callback=None, progress_callback_num=None
    ) -> bool:
        """Loads the page url from the webdriver."""
        pause = self.request_pause
        if self.random_pauses:
            pause += random.randint(-5, 5)

        logging.info(f"[get page] Pausing for {pause} seconds")
        progress_callback.emit(f"[get page] Pausing for {pause} seconds")
        sleep(pause)

        logging.info(f"[get page] getting page data {url}...")
        progress_callback.emit(f"[get page] getting page data {url}...")
        t = time()
        try:
            self.driver.get(url)
        except TimeoutException as e:
            logging.error(
                f"[get page] The webdriver reached the timeout limit at {self.page_timeout} seconds."
            )
            progress_callback.emit(
                f"[get page] The webdriver reached the timeout limit at {self.page_timeout} seconds"
            )
            self.driver.execute_script("window.stop();")
            return True
        except Exception as e:
            logging.critical(e)
            logging.critical("[get page] The webdriver failed to get the page.")
            progress_callback.emit("[get page] The webdriver failed to get the page.")
            return False

        logging.info(
            f"[get page] Page {url} was loaded in {round(time()-t, 3)} seconds"
        )
        progress_callback.emit(
            f"[get page] Page {url} was loaded in {round(time()-t, 3)} seconds"
        )

        return True

    def parse_funding_page(
        self,
        id: str,
        last_date: str = "",
        progress_callback=None,
        progress_callback_num=None,
    ) -> bool:
        """
        Parse as page for the 'Funds' sheet and save  it to the object data instance.
        The page is loaded for a specific company id, and the data is saved to the object's
        data attribute under 'funds' -> {id}
        """

        # load the funds page for this id
        if not self._get_page(
            f"{self.base_url_funds}{id}.html",
            progress_callback=progress_callback,
            progress_callback_num=progress_callback_num,
        ):
            return False

        # parse the html
        soup = None
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            logging.error(e)
            logging.error(
                f"[parse funds] Something went wrong while parsing the funds page for {id}"
            )
            progress_callback.emit(
                f"[parse funds] Something went wrong while parsing the funds page for {id}"
            )
            return False

        funds_data = self.data["funds"]

        ###########################
        # get price table
        try:
            prices = {}
            table = soup.find("table", {"class": "lsjz"})

            tbody = table.find("tbody")
            rows = tbody.find_all("tr")

            for row in rows:
                attr = row.find_all("td")
                prices[attr[0].text.strip()] = attr[1].text.strip()

            funds_data[id] = prices

            logging.info(
                f"[parse funds] Retrieved funds history for {id} {prices.keys()}"
            )
            progress_callback.emit(
                f"[parse funds] Retrieved funds history for {id} {prices.keys()}"
            )

        except Exception as e:
            logging.critical(e)
            logging.critical(
                f"[parse funds] Something went wrong while parsing the page html.\
                Make sure you aren't being blocked from loading the page and are using a sufficient pause between requests."
            )
            progress_callback.emit(
                f"[parse funds] Something went wrong while parsing the page html.\
                Make sure you aren't being blocked from loading the page and are using a sufficient pause between requests."
            )
            return False
        return True

    def parse_ranking_page(
        self, id: str, progress_callback, progress_callback_num
    ) -> bool:
        """
        Parse a page for the 'Ranking' sheet and save it to the object data instance.
        The page is loaded for a specific company id, and the data is saved to the object's
        data attribute under 'ranking' -> {id}
        """

        # load the ranking page for this id
        if not self._get_page(
            f"{self.base_url_ranking}{id}.html",
            progress_callback=progress_callback,
            progress_callback_num=progress_callback_num,
        ):
            return False

        # parse the html
        soup = None
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            logging.error(e)
            logging.error(
                f"[parse ranking] Something went wrong while parsing the ranking page for {id}"
            )
            progress_callback.emit(
                f"[parse ranking] Something went wrong while parsing the ranking page for {id}"
            )
            return False

        ranking_data = self.data["ranking"]
        ranking_data[id] = []

        ###########################
        # get the top info bar
        try:
            info = soup.find("div", {"class": "bs_jz"})

            # get the SECOND label from the right column's row1
            label = (
                (info.find("div", {"class": "col-right"}))
                .find("p", {"class": "row1"})
                .find_all("label")[1]
            )

            label_texts = [s.strip() for s in label.text.strip().split("\n")]

            # 1. get the date
            date = label_texts[0]
            date = date[date.find("（") + 1 : date.find("）")]
            ranking_data[id].append(date)

            # get the initial prices
            prices = label_texts[2]
            prices = prices.split(" ( ")
            # 2.
            ranking_data[id].append(prices[0])
            # 3.
            ranking_data[id].append(prices[1].strip(" )"))

            #################################
            # get table with historical prices
            table = (
                (soup.find("div", {"id": "jdzftable"}))
                .find("div", {"class": "jdzfnew"})
                .find_all("ul")
            )

            for tbl_element in table[1:-1]:
                ranking_data[id].append(tbl_element.find_all("li")[1].text.strip())

            # name = get_name_from_id(id)
            # temp = ranking_data[id]
            # ranking_data[id] = {}
            # ranking_data[id]['name'] = name
            # ranking_data[id]['info'] = temp

            self.updated = True

            logging.info(f"Fetched ranking data for {id} with info {ranking_data[id]}")
            progress_callback.emit(
                f"Fetched ranking data for {id} with info {ranking_data[id]}"
            )
        except Exception as e:
            logging.critical(e)
            logging.critical(
                f"[parse ranking] Something went wrong while parsing the page html.\
                Make sure you aren't being blocked from loading the page and are using a sufficient pause between requests."
            )
            progress_callback.emit(
                f"[parse ranking] Something went wrong while parsing the page html.\
                Make sure you aren't being blocked from loading the page and are using a sufficient pause between requests."
            )
            return False
        return True

    def parse_top(
        self, url, progress_callback=None, progress_callback_num=None
    ) -> bool:
        """
        Parses a top rankings page by retrieving the entire table from the given url.
        All of the data gets stored into data['top'] as a list of two-tuples,
        (<id>, <name>)
        """
        if not self._get_page(
            url,
            progress_callback=progress_callback,
            progress_callback_num=progress_callback_num,
        ):
            return False

        # parse the html
        soup = None
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            logging.error(e)
            logging.error(
                f"[parse top] Something went wrong while parsing the top ranking page"
            )
            progress_callback.emit(
                f"[parse top] Something went wrong while parsing the top ranking page"
            )
            return False

        top_ids = self.data["top"]

        try:
            body = (soup.find("table", {"id": "dbtable"})).find("tbody")

            rows = body.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                id = (cols[2]).find("a").text.strip()
                name = (cols[3]).find("a").get("title")
                # link = (cols[3]).find("a").get("href")
                # name = (cols[3]).find("a").text.strip()
                top_ids.append([id, name])

            self.updated = True

            logging.info(f"Fetched top ranking data {len(top_ids)}")
            progress_callback.emit(f"Fetched top ranking data {len(top_ids)}")
        except Exception as e:
            logging.critical(e)
            logging.critical(
                f"[parse top] Something went wrong while parsing the page html.\
                Make sure you aren't being blocked from loading the page and are using a sufficient pause between requests."
            )
            progress_callback.emit(
                f"[parse top] Something went wrong while parsing the page html.\
                Make sure you aren't being blocked from loading the page and are using a sufficient pause between requests."
            )
            return False
        return True

    def export_data(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
            logging.info(f"[export web scraper data] saved data to {path}")

    def click_next_page(self):
        self.funds_page += 1
        self.driver.find_element_by_css_selector("#pnum").send_keys(
            str(self.funds_page)
        )
        self.driver.find_element_by_css_selector(".pgo").click()
        time.sleep(3)

    def stop_driver(self):
        self.driver.quit()
        self.is_on = False
