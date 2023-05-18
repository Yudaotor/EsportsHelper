import sys
from time import sleep, strftime
from traceback import format_exc

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager
from plyer import notification
from retrying import retry
from rich import print
from EsportsHelper.I18n import _, _log
from EsportsHelper.Logger import delimiterLine


class Utils:
    def __init__(self, config):
        self.config = config
        pass

    def errorNotify(self, error):
        """
        Sends error notifications to selected channels based on the user's configuration settings.

        Args:
            error (str): The error message to be included in the notification.

        """
        notifyType = self.config.notifyType
        needDesktopNotify = self.config.desktopNotify
        connectorUrl = self.config.connectorDropsUrl
        language = self.config.language
        if notifyType in ["all", "error"]:
            if needDesktopNotify:
                try:
                    notification.notify(
                        title=_log("小傻瓜，出事啦", lang=language),
                        message=f"Error Message: {error}",
                        timeout=30
                    )
                    print(_("错误提醒发送成功", color="green", lang=language))
                    log.info(_log("错误提醒发送成功", lang=language))
                except Exception as e:
                    print(_("错误提醒发送失败", color="red", lang=language))
                    log.error(_log("错误提醒发送失败", lang=language))
                    log.error(format_exc())

            if connectorUrl != "":
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                try:
                    if "https://oapi.dingtalk.com" in connectorUrl:
                        data = {
                            "msgtype": "link",
                            "link": {
                                "text": "Alert: Drop farming stopped",
                                "title": error,
                                "picUrl": "",
                                "messageUrl": ""
                            }
                        }
                        s.post(connectorUrl, json=data)

                    elif "https://discord.com/api/webhooks" in connectorUrl:
                        embed = {
                            "title": "Alert: Drop farming stopped",
                            "description": f"{error}",
                            "image": {"url": f""},
                            "thumbnail": {"url": f""},
                            "color": 6676471,
                        }
                        params = {
                            "username": "EsportsHelper",
                            "embeds": [embed]
                        }
                        s.post(connectorUrl, headers={
                            "Content-type": "application/json"}, json=params)

                    else:
                        params = {
                            "text": f"发生错误停止获取Drop{error}",
                        }
                        s.post(connectorUrl, headers={
                            "Content-type": "application/json"}, json=params)

                    log.info(_log("异常提醒成功", lang=language))
                    print(_("异常提醒成功", color="green", lang=language))
                except Exception:
                    print(_("异常提醒失败", color="red", lang=language))
                    log.error(_log("异常提醒失败", lang=language))
                    log.error(format_exc())

    def debugScreen(self, driver, lint="normal"):
        """
        Function Name: debugScreen
        Input:
            - driver: webdriver object
            - lint: string (default: "")
        Output: None
        Purpose: Saves a screenshot of the current webpage for debugging purposes.
                 The screenshot is saved to ./logs/pics/ directory with a timestamp and a lint identifier.
                 If the lint parameter is not specified, an empty string will be used as the identifier.
        """
        try:
            if self.config.debug:
                sleep(3)
                driver.save_screenshot(f"./logs/pics/{strftime('%b-%d-%H-%M-%S')}-{lint}.png")
                log.info(f'{lint}-{_log("调试截图成功", lang=self.config.language)}')
        except Exception:
            log.error(f'{lint}-{_log("调试截图失败", lang=self.config.language)}')
            log.error(format_exc())

    def info(self):
        version = VersionManager.getVersion()
        githubUrl = "https://github.com/Yudaotor/EsportsHelper"
        VersionManager(self.config).checkVersion()
        if self.config.language == "zh_CN":
            delimiterLine()
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]        "
                  f"感谢使用 [cyan]电竞助手[/cyan] v{version}!        "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 12}[/bold yellow] "
                  f"本程序开源于github链接地址如下: "
                  f"[bold yellow]{'=' * 12}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]   "
                  f"{githubUrl}     "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"如觉得不错的话可以进上面链接请我喝杯咖啡支持下. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]  "
                  f"如需关闭请勿直接右上角X关闭，请按Ctrl+C来关闭. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            delimiterLine()
            print()
        elif self.config.language == "en_US":
            delimiterLine()
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow] "
                  f"Thanks for using [cyan]EsportsHelper[/cyan] v{version}!  "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]   "
                  f"The program is open source at GitHub  "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]    "
                  f"{githubUrl}    [bold yellow]{'=' * 4}"
                  f">_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]      "
                  f"If you like it, please give me a star      "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            delimiterLine()
            print()
        elif self.config.language == "zh_TW":
            delimiterLine()
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]        "
                  f"感謝使用 [cyan]電競助手[/cyan] v{version}!        "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 12}[/bold yellow] "
                  f"本程式開源於github連結地址如下: "
                  f"[bold yellow]{'=' * 12}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]   "
                  f"{githubUrl}     "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"如覺得不錯的話可以進上面連結請我喝杯咖啡支援下. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"請在使用前[red]閱讀教程檔案[/red], 以確保你的配置符合要求! "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]  "
                  f"如需關閉請勿直接右上角X關閉，請按Ctrl+C來關閉. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            delimiterLine()
            print()

    def getOverrideFile(self):
        """
        Function Name: getOverrideFile
        Output: Dictionary containing overrides from a remote file
        Purpose: Retrieve overrides from a remote file and return them as a dictionary
        """
        try:
            OVERRIDES = {}
            req = requests.session()
            headers = {'Content-Type': 'text/plain; charset=utf-8',
                       'Connection': 'close'}
            try:
                remoteOverrideFile = req.get(
                    "https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt", headers=headers)
            except Exception:
                log.error(_log("从github获取override文件失败, 将尝试从gitee获取", lang=self.config.language))
                print(_("从github获取override文件失败, 将尝试从gitee获取", color="red", lang=self.config.language))
                remoteOverrideFile = req.get(
                    "https://gitee.com/yudaotor/EsportsHelper/raw/main/override.txt", headers=headers)
            if remoteOverrideFile.status_code == 200:
                override = remoteOverrideFile.text.split(",")
                first = True
                for o in override:
                    temp = o.split("|")
                    if len(temp) == 2:
                        if first:
                            first = False
                        else:
                            temp[0] = temp[0][1:]
                        OVERRIDES[temp[0]] = temp[1]
                log.info(_log("获取override文件成功", lang=self.config.language))
                print(_("获取override文件成功", color="green", lang=self.config.language))
                return OVERRIDES
            else:
                print(_("获取override文件失败", color="red", lang=self.config.language))
                log.error(_log("获取override文件失败", lang=self.config.language))
                input(_log("按回车键退出", lang=self.config.language))
                sysQuit(e=_log("获取override文件失败", lang=self.config.language))
        except Exception:
            log.error(_log("获取override文件失败", lang=self.config.language))
            print(_("获取override文件失败", color="red", lang=self.config.language))
            input(_log("按回车键退出", lang=self.config.language))
            sysQuit(e=_log("获取override文件失败", lang=self.config.language))


def desktopNotify(poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg, dropLocale):
    """
    Desktop notification function that sends a notification to the user's desktop.

    Args:
    poweredByImg (str): The image URL of the company that powers the event.
    productImg (str): The image URL of the product being dropped.
    unlockedDate (str): The date and time when the drop will be unlocked.
    eventTitle (str): The title of the event.
    dropItem (str): The name of the dropped item.
    dropItemImg (str): The image URL of the dropped item.
    dropLocale (str): The location where the drop will occur.

    """
    try:
        notification.notify(
            title="New drop!",
            message=f"BY {eventTitle} GET{dropItem} ON{dropLocale} {unlockedDate}",
            timeout=30
        )
        log.info("Desktop notification sent successfully")
    except Exception:
        log.error("Desktop notification failed")
        log.error(format_exc())


def sysQuit(driver=None, e=None):
    """
    Function: sysQuit
    Description: Safely quits the webdriver and exits the program.
    Input:
        - driver: Webdriver instance to be quit
        - e: Exception that occurred (optional)
    Output: None
    """
    sleep(1)
    if driver:
        driver.quit()
    log.error(e)
    log.info("------Quit------")
    sys.exit()


def getMatchName(url: str) -> str:
    """
    Returns the name of the match corresponding to the given URL.

    Args:
        url (str): A string that represents a URL.

    Returns:
        str: A string that represents the name of the match.
    """
    match = url.split('/')[-2] if url.split('/')[-2] != "live" else url.split('/')[-1]
    match = "cblol" if match == "cblol-brazil" else match
    match = "ljl" if match == "ljl-japan" else match
    match = "tft_rising_legends" if match == "tft_esports" else match
    match = match.upper()
    return match


# Repeat the attempt to fetch the page up to 4 times,
# and the wait time is based on 2 minutes, each time incremented by 2 minutes
@retry(stop_max_attempt_number=4, wait_incrementing_increment=120000, wait_incrementing_start=120000)
def getLolesportsWeb(driver, language) -> None:
    """
    Retrieves the Lolesports website using the provided driver. If an exception occurs while accessing the website,
    it retries for a maximum of four times, incrementing the wait time between each attempt by two minutes.

    Args:
    - driver (selenium.webdriver.remote.webdriver.WebDriver): The driver to use for accessing the Lolesports website
    - language (str): The language to use for log
    """
    try:
        driver.get(
            "https://lolesports.com/schedule?leagues=msi,lcs,north_american_challenger_league,"
            "lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,"
            "ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,emea_masters,"
            "lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,"
            "hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,"
            "ljl_academy,lck_challengers_league,cblol_academy,north_regional_league,"
            "south_regional_league,tft_esports")

    except Exception:
        print(_("获取LoLEsports网站失败，正在重试...", color="red", lang=language))
        log.error(_log("获取LoLEsports网站失败，正在重试...", lang=language))
        driver.get(
            "https://lolesports.com/schedule?leagues=msi,lcs,north_american_challenger_league,"
            "lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,"
            "ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,emea_masters,"
            "lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,"
            "hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,"
            "ljl_academy,lck_challengers_league,cblol_academy,north_regional_league,"
            "south_regional_league,tft_esports")


def getSleepPeriod(config):
    """
    Get sleep period from config file
    """
    return [int(period.split("-")[0]) for period in config.sleepPeriod if period], \
           [int(period.split("-")[1]) for period in config.sleepPeriod if period]


@retry(stop_max_attempt_number=4, wait_incrementing_increment=10000, wait_incrementing_start=10000)
def checkRewardPage(driver, language):
    """
    Check if the reward page exists.

    Args:
        driver: Selenium WebDriver instance.
        language: The language used for logging.

    Returns:
        - None if the reward page does not exist.
        - Returns without any value if the reward page exists.
    """
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "div.name")))
    except Exception:
        try:
            # Special cases where there is no drop ---- new account
            wait.until(ec.presence_of_element_located(
                (By.XPATH, "//div[text()='NO DROPS YET']")))
        except Exception:
            driver.refresh()
            print(_("获取reward网站失败，正在重试...", color="red", lang=language))
            log.error(_log("获取reward网站失败，正在重试...", lang=language))
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.name")))
        else:
            return


def getMatchTeams(teams, language):
    """
    Get match teams from stream title
    """
    if teams and ("|" in teams or "-" in teams):
        delimiter = "|" if "|" in teams else "-"
        words = teams.split(delimiter)
        for word in words:
            if "vs" in word.lower():
                teams = word
                break
            else:
                teams = words[0]
    else:
        teams = _log("出错, 未知", lang=language)
    return teams


