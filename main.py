from time import sleep
from traceback import format_exc

from EsportsHelper.Config import config
from EsportsHelper.I18n import i18n
from EsportsHelper.Logger import log
from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.Match import Match
from EsportsHelper.Utils import Utils, getLolesportsWeb, sysQuit
from EsportsHelper.Webdriver import Webdriver
from rich import print
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

global driver
_ = i18n.getText
_log = i18n.getLog


def init():
    """
    Initialize the program by creating a webdriver, setting the window size, opening the Lolesports webpage, and switching the language to English.
    """
    global driver
    # Generate webdriver
    try:
        driver = Webdriver().createWebdriver()
    except TypeError:
        driver = None
        log.error(format_exc())
        print(_("生成WEBDRIVER失败!", color="red"))
        print(_("无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开",
                color="red"))
        print(_("如果还不行请尝试重装谷歌浏览器", color="red"))
        input(_log("按回车键退出"))
        sysQuit(driver)
    except WebDriverException:
        driver = None
        log.error(format_exc())
        print(_("生成WEBDRIVER失败!", color="red"))
        print(_("是否有谷歌浏览器?\n是否打开着谷歌浏览器?请关闭后再次尝试", color="red"))
        print(_("如果还不行请尝试重装谷歌浏览器", color="red"))
        input(_log("按回车键退出"))
        sysQuit(driver)
    except Exception:
        driver = None
        log.error(format_exc())
        print(_("生成WEBDRIVER失败!", color="red"))
        print(_("是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用", color="red"))
        print(_("如果还不行请尝试重装谷歌浏览器", color="red"))
        input(_log("按回车键退出"))
        sysQuit(driver)
    # Set the window size
    driver.set_window_size(960, 768)
    driver.set_window_position(0, 0)
    # Open lolesports page
    try:
        getLolesportsWeb(driver)
    except Exception:
        log.error(format_exc())
        log.error(
            _log("无法打开Lolesports网页，网络问题，将于3秒后退出..."))
        print(_("无法打开Lolesports网页，网络问题，将于3秒后退出...", color="red"))
        sysQuit(driver, _log("无法打开Lolesports网页，网络问题，将于3秒后退出..."))
    # Switch web language to English
    try:
        wait = WebDriverWait(driver, 20)
        languageButton = wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='riotbar:localeswitcher:button-toggleLocaleMenu']")))
        languageButton.click()
        enUSButton = wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='riotbar:localeswitcher:dropdown'] > li:nth-child(1) > a")))
        enUSButton.click()
        log.info(_log("切换网页语言成功"))
        print(_("切换网页语言成功", color="green"))
    except TimeoutException:
        log.error(_log("切换网页语言失败"))
        print(_("切换网页语言失败", color="green"))
        log.error(format_exc())
    except Exception:
        log.error(_log("切换网页语言失败"))
        print(_("切换网页语言失败", color="green"))
        log.error(format_exc())


def login():
    """
    The login function, which logs in with the given configuration information and outputs the login result.
    """
    loginHandler = LoginHandler(driver=driver)
    if config.userDataDir == "":
        tryLoginTimes = 4
        while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name") and tryLoginTimes > 0:
            try:
                if loginHandler.automaticLogIn(config.username, config.password):
                    pass
                else:
                    tryLoginTimes = tryLoginTimes - 1
                    if tryLoginTimes <= 0:
                        print(f'--{_("无法登录，账号密码可能错误或者网络出现问题", color="red")}')
                        sysQuit(driver, _log("无法登录，账号密码可能错误或者网络出现问题"))
                    else:
                        log.error(_log("5秒后开始重试"))
                        print(f'--{_("5秒后开始重试", color="yellow")}')
                        sleep(5)
            except Exception:
                log.error(format_exc())
                print(f'--{_("出现异常,登录失败", color="red")}')
                sysQuit(driver, _log("出现异常,登录失败"))

        log.info(_log("好嘞 登录成功"))
        print(f'--{_("好嘞 登录成功", color="green")}')
    else:
        loginHandler.userDataLogin()
        log.info(_log("使用浏览器缓存 自动登录成功"))
        print(f'--{_("使用浏览器缓存 自动登录成功", color="green")}')


def watch():
    Match(driver=driver).watchMatches(delay=config.delay, maxRunHours=config.maxRunHours)


def main():
    """
    Main function to run the EsportsHelper program.

    Parses command line arguments, initializes the configuration and utility objects,
    initializes the webdriver, logs in, watches the match and prints the completion message.

    """
    global driver
    # Print the banner information
    utils = Utils()
    utils.info()

    init()
    sleep(3)
    login()
    sleep(1)
    watch()
    print(_("观看结束", color="green"))
    log.info(_log("观看结束"))


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sysQuit(driver, "Exit")
    except Exception:
        sysQuit(driver, format_exc())
