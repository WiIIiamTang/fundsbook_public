import logging
from datetime import date, datetime
from .web_scraper import EastMoneyFundScraper
from .workbook_manager import WorkbookManager

# TODO: clean up this file (old code)


def read_funds(
    workbook_manager: WorkbookManager, progress_callback, progress_callback_num
) -> None:
    """Perform all reading tasks (retrieve missing cells that need to be updated)"""
    workbook_manager.read_funds(
        progress_callback=progress_callback, progress_callback_num=progress_callback_num
    )
    progress_callback_num.emit(len(workbook_manager.missing_funds))
    progress_callback.emit("PROG:FUNDS SHEET")


def read_rankings(
    workbook_manager: WorkbookManager, progress_callback, progress_callback_num
) -> None:
    workbook_manager.read_rankings(
        progress_callback=progress_callback, progress_callback_num=progress_callback_num
    )
    progress_callback_num.emit(len(workbook_manager.ranking_ids))
    progress_callback.emit("PROG: RANKINGS SHEET")


def scrape_funds(
    scraper: EastMoneyFundScraper,
    missing_funds: dict,
    ranking_ids: list,
    run_threads,
    progress_callback,
    progress_callback_num,
) -> None:
    """Perform all web scraping tasks"""
    for funds_id in missing_funds.keys():
        scraper.parse_funding_page(
            funds_id,
            progress_callback=progress_callback,
            progress_callback_num=progress_callback_num,
        )
        if not run_threads.flag:
            logging.info("Stopping thread")
            progress_callback.emit("Stopping thread")
            return
        progress_callback_num.emit(-1)


def scrape_rankings(
    scraper: EastMoneyFundScraper,
    missing_funds: dict,
    ranking_ids: list,
    top: bool = False,
    run_threads=None,
    progress_callback=None,
    progress_callback_num=None,
) -> None:
    if not top:
        for ranking_id in ranking_ids:
            scraper.parse_ranking_page(
                str(ranking_id.value),
                progress_callback=progress_callback,
                progress_callback_num=progress_callback_num,
            )
            if not run_threads.flag:
                logging.info("Stopping thread")
                progress_callback.emit("Stopping thread")
                return
            progress_callback_num.emit(-1)
    else:
        for ranking_id in ranking_ids:
            scraper.parse_ranking_page(
                str(ranking_id),
                progress_callback=progress_callback,
                progress_callback_num=progress_callback_num,
            )
            if not run_threads.flag:
                logging.info("Stopping thread")
                progress_callback.emit("Stopping thread")
                return
            progress_callback_num.emit(-1)


def write_funds(
    workbook_manager: WorkbookManager,
    funds_data: dict,
    ranking_data: dict,
    progress_callback,
    progress_callback_num,
) -> None:
    workbook_manager.write_funds(
        funds_data=funds_data,
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )


def write_rankings(
    workbook_manager: WorkbookManager,
    funds_data: dict,
    ranking_data: dict,
    sheet_name: str = None,
    ids_override: list = None,
    progress_callback=None,
    progress_callback_num=None,
) -> None:
    if sheet_name:
        workbook_manager.write_rankings(
            ranking_data,
            sheet_name,
            ids_override,
            progress_callback=progress_callback,
            progress_callback_num=progress_callback_num,
        )
    else:
        workbook_manager.write_rankings(
            ranking_data,
            progress_callback=progress_callback,
            progress_callback_num=progress_callback_num,
        )


def start_funds_job(excel_file_name: str = "FundsBook.xlsx", data: dict = None) -> None:

    """Starts all tasks in order. Passes the data to the correct functions."""

    logging.info("--- web scraper start")

    # init classes
    workbook_manager = WorkbookManager(excel_file_name)
    scraper = EastMoneyFundScraper(["--headless"])
    scraper.start_driver()

    # read, send missing data to scraper, write new data
    read_funds(workbook_manager)
    if not data:
        scrape_funds(
            scraper, workbook_manager.missing_funds, workbook_manager.ranking_ids
        )

    if not data:
        write_funds(workbook_manager, scraper.data["funds"], scraper.data["ranking"])
    else:
        write_funds(workbook_manager, data["funds"], data["ranking"])

    # clean up
    scraper.export_data(f"web_scraper_data_{date.today()}_funds.json")
    workbook_manager.close()
    scraper.stop_driver()

    logging.info("--- web scraper done")


def start_rankings_job(
    excel_file_name: str = "FundsBook.xlsx", data: dict = None
) -> None:

    """Starts all tasks in order. Passes the data to the correct functions."""

    logging.info("--- web scraper start")

    # init classes
    workbook_manager = WorkbookManager(excel_file_name)
    scraper = EastMoneyFundScraper(["--headless"])
    scraper.start_driver()

    # read, send missing data to scraper, write new data
    read_rankings(workbook_manager)

    if not data:
        scrape_rankings(
            scraper, workbook_manager.missing_funds, workbook_manager.ranking_ids
        )

    if not data:
        write_rankings(workbook_manager, scraper.data["funds"], scraper.data["ranking"])
    else:
        write_rankings(workbook_manager, data["funds"], data["ranking"])

    # clean up
    if not data:
        scraper.export_data(f"web_scraper_data_{date.today()}_rankings.json")
    workbook_manager.close()
    scraper.stop_driver()

    logging.info("--- web scraper done")


def start_top_job(
    excel_file_name: str = "FundsBook_sample.xlsx",
    sheet_name: str = "top50",
    data: dict = None,
    pn: int = 50,
    hash: str = "tall",
    date_low: str = "20200721",
    date_high: str = "20210721",
) -> None:

    """Starts all tasks in order. Passes the data to the correct functions."""

    logging.info("--- web scraper start")

    # init classes
    workbook_manager = WorkbookManager(excel_file_name)
    scraper = EastMoneyFundScraper(["--headless"])
    scraper.start_driver()
    scraper.request_pause = 7

    # write new data
    url = f"http://fund.eastmoney.com/data/fundranking.html#{hash};c0;r;sjnzf;pn{pn};ddesc;qsd{date_low};qed{date_high};qdii;zq;gg;gzbd;gzfs;bbzt;sfbb"
    if not data:
        scraper.parse_top(url)
        scrape_rankings(
            scraper, {}, ranking_ids=[a[0] for a in scraper.data["top"]], top=True
        )

    if not data:
        write_rankings(
            workbook_manager,
            scraper.data["funds"],
            scraper.data["ranking"],
            sheet_name,
            scraper.data["top"],
        )
    else:
        write_rankings(
            workbook_manager, data["funds"], data["ranking"], sheet_name, data["top"]
        )

    # clean up
    if not data:
        scraper.export_data(f"web_scraper_data_{date.today()}_top.json")
    workbook_manager.close()
    scraper.stop_driver()

    logging.info("--- web scraper done")


#################################################################################################################################
#################################################################################################################################


def start_rankings_job_thread_worker(
    scraper, workbook_manager, run_threads, progress_callback, progress_callback_num
):
    if not run_threads.flag:
        return

    logging.info("--- web scraper start rankings")
    progress_callback.emit("--- web scraper start rankings")

    # read, send missing data to scraper, write new data
    read_rankings(
        workbook_manager,
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )
    scrape_rankings(
        scraper,
        workbook_manager.missing_funds,
        workbook_manager.ranking_ids,
        run_threads=run_threads,
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )
    if not run_threads.flag:
        return
    write_rankings(
        workbook_manager,
        scraper.data["funds"],
        scraper.data["ranking"],
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )

    logging.info("--- web scraper done rankings")
    progress_callback.emit("--- web scraper done rankings")


def start_funds_job_thread_worker(
    scraper, workbook_manager, run_threads, progress_callback, progress_callback_num
):
    if not run_threads.flag:
        return

    logging.info("--- web scraper start funds")
    progress_callback.emit("--- web scraper start funds")

    # read, send missing data to scraper, write new data
    read_funds(
        workbook_manager,
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )
    scrape_funds(
        scraper,
        workbook_manager.missing_funds,
        workbook_manager.ranking_ids,
        run_threads=run_threads,
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )
    if not run_threads.flag:
        return
    write_funds(
        workbook_manager,
        scraper.data["funds"],
        scraper.data["ranking"],
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )

    logging.info("--- web scraper done funds")
    progress_callback.emit("--- web scraper done funds")


def start_top_job_thread_worker(
    scraper,
    workbook_manager,
    run_threads,
    progress_callback,
    progress_callback_num,
    sheet_name="top50混合",
    pn: int = 2,
    hash: str = "tall",
    date_low: str = "20200721",
    date_high: str = "20210721",
):
    if not run_threads.flag:
        return
    logging.info("--- web scraper start top")
    progress_callback.emit("--- web scraper start top")

    # write new data
    url = f"http://fund.eastmoney.com/data/fundranking.html#{hash};c0;r;sjnzf;pn{pn};ddesc;qsd{date_low};qed{date_high};qdii;zq;gg;gzbd;gzfs;bbzt;sfbb"
    scraper.parse_top(
        url,
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )
    progress_callback_num.emit(len(scraper.data["top"]))
    progress_callback.emit(f"PROG:TOP50 SHEET {sheet_name}")
    scrape_rankings(
        scraper,
        {},
        ranking_ids=[a[0] for a in scraper.data["top"]],
        top=True,
        run_threads=run_threads,
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )
    if not run_threads.flag:
        return
    write_rankings(
        workbook_manager,
        scraper.data["funds"],
        scraper.data["ranking"],
        sheet_name,
        scraper.data["top"].copy(),
        progress_callback=progress_callback,
        progress_callback_num=progress_callback_num,
    )

    logging.info("--- web scraper done top")
    progress_callback.emit("--- web scraper done top")


def save(scraper, workbook_manager, progress_callback):
    scraper.export_data(f"web_scraper_data_{date.today()}_all.json")
    progress_callback.emit("saved web scraper data")


def start(
    scraper,
    workbook_manager,
    run_threads,
    save_data,
    funds,
    rankings,
    top,
    pn,
    progress_callback,
    progress_callback_num,
):

    if funds:  # update all holding fund's daily prices in sheet 基金日记
        start_funds_job_thread_worker(
            scraper,
            workbook_manager,
            run_threads,
            progress_callback,
            progress_callback_num,
        )

    if rankings:  # update all holding fund's info in sheet 基金排队
        start_rankings_job_thread_worker(
            scraper,
            workbook_manager,
            run_threads,
            progress_callback,
            progress_callback_num,
        )

    if (
        top
    ):  # update top 50 fund's position in reach 5 categories in sheets top50混合, top50股票 etc
        #
        top50Name = [
            ("top50混合", "thh"),
            ("top50股票", "tgp"),
            ("top50指数", "tzs"),
            ("top50债券", "tzq"),
            ("top50QDII", "tqdii"),
        ]
        # top50Name = [('top50混合','thh')]
        #
        today = datetime.now()
        one_year_ago = today.replace(year=today.year - 1)

        for index, tuple in enumerate(top50Name):  # loop through all 5 sheets
            element_one = tuple[0]  # sheet name
            element_two = tuple[1]  # hash tag
            start_top_job_thread_worker(
                scraper,
                workbook_manager,
                run_threads,
                progress_callback,
                progress_callback_num,
                sheet_name=element_one,
                pn=pn,
                hash=element_two,
                date_low=one_year_ago.strftime("%Y%m%d"),
                date_high=today.strftime("%Y%m%d"),
            )
            print(scraper.data)
            scraper.data = {"ranking": {}, "funds": {}, "top": []}
            workbook_manager.missing_funds = None
            workbook_manager.ranking_ids = None
            print()  # print a blank line for reading clarity

    if not run_threads.flag:
        logging.info(
            "The workbook tasks thread was manually stopped and did not finish correctly."
        )
        progress_callback.emit(
            "The workbook tasks thread was manually stopped and did not finish correctly."
        )
        return False

    if save_data:
        save(scraper, workbook_manager, progress_callback)

    workbook_manager.close()
    return True


def buy_funds_from_workbook(
    workbook_manager, id, amount, date, progress_callback, progress_callback_num
):
    logging.info(f"(buy funds) trying to buy funds {id} {amount} {date}")
    workbook_manager.buy_funds(
        id, amount, date, sheet="基金日记", progress_callback=progress_callback
    )
    workbook_manager.close()
    return True
