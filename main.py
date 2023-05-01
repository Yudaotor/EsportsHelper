import argparse
from time import sleep
from traceback import format_exc

from EsportsHelper.Config import Config
from EsportsHelper.Logger import log
from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.Match import Match
from EsportsHelper.Utils import Utils, _, _log, getLolesportsWeb, sysQuit
from EsportsHelper.Webdriver import Webdriver
from rich import print
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

global driver


def init(config):
    """
    Initialize the program by creating a webdriver, setting the window size, opening the Lolesports webpage, and switching the language to English.

    Args:
        config: A Config object that contains program configuration settings.

    """
    global driver
    # Generate webdriver
    try:
        driver = Webdriver(config).createWebdriver()
    except TypeError:
        driver = None
        log.error(format_exc())
        print(_("生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开",
              color="red", lang=config.language))
        input(_log("按回车键退出", lang=config.language))
        sysQuit(driver)
    except WebDriverException:
        driver = None
        log.error(format_exc())
        print(_("生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是否打开着谷歌浏览器?请关闭后再次尝试",
              color="red", lang=config.language))
        input(_log("按回车键退出", lang=config.language))
        sysQuit(driver)
    except Exception:
        driver = None
        log.error(format_exc())
        print(_("生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用",
              color="red", lang=config.language))
        input(_log("按回车键退出", lang=config.language))
        sysQuit(driver)
    # Set the window size
    driver.set_window_size(960, 768)
    # Open lolesports page
    try:
        getLolesportsWeb(driver)
    except Exception:
        log.error(format_exc())
        log.error(
            _log("无法打开Lolesports网页，网络问题，将于3秒后退出...", lang=config.language))
        print(_("无法打开Lolesports网页，网络问题，将于3秒后退出...",
              color="red", lang=config.language))
        sysQuit(driver, _log("无法打开Lolesports网页，网络问题，将于3秒后退出..."))
    # Switch web language to English
    try:
        wait = WebDriverWait(driver, 20)
        languageButton = wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "#riotbar-right-content > div._1K9T69nrXajaz_b4HNuhtI.riotbar-locale-switcher > div > a")))
        languageButton.click()
        driver.find_element(by=By.CSS_SELECTOR,
                            value="#riotbar-right-content > div._1K9T69nrXajaz_b4HNuhtI.riotbar-locale-switcher > div._2iYBTCEu1pbDL1lBawLJ3O.locale-switcher-dropdown > ul > li:nth-child(1) > a").click()
        log.info(_log("切换语言成功", lang=config.language))
    except TimeoutException:
        log.error(_log("切换语言失败", lang=config.language))
        log.error(format_exc())
    except Exception:
        log.error(_log("切换语言失败", lang=config.language))
        log.error(format_exc())


def login(config):
    """
    The login function, which logs in with the given configuration information and outputs the login result.

    Args:
        config: A Config object that contains the configuration information required for login.
    """
    loginHandler = LoginHandler(log=log, driver=driver, config=config)
    if config.userDataDir == "":
        tryLoginTimes = 4
        while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
            try:
                loginHandler.automaticLogIn(config.username, config.password)
            except TimeoutException:
                tryLoginTimes = tryLoginTimes - 1
                if tryLoginTimes <= 0:
                    sysQuit(driver, _log("无法登陆，账号密码可能错误或者网络出现问题"))
                    print(_("无法登陆，账号密码可能错误或者网络出现问题",
                          color="red", lang=config.language))

                log.error(_log("自动登录失败,检查网络和账号密码", lang=config.language))
                print(_("自动登录失败,检查网络和账号密码", color="red", lang=config.language))
                sleep(5)
                log.error(_log("开始重试", lang=config.language))

        log.info(_log("好嘞 登录成功", lang=config.language))
        print(_("好嘞 登录成功", color="green", lang=config.language))
    else:
        loginHandler.userDataLogin()
        log.info(_log("使用浏览器缓存 自动登录成功", lang=config.language))
        print(_("使用浏览器缓存 自动登录成功", color="green", lang=config.language))


def watch(config):
    Match(log=log, driver=driver, config=config).watchMatches(
        delay=config.delay, maxRunHours=config.maxRunHours)


def main():
    """
    Main function to run the EsportsHelper program.

    Parses command line arguments, initializes the configuration and utility objects,
    initializes the webdriver, logs in, watches the match and prints the completion message.

    """
    global driver
    # 解析配置参数
    parser = argparse.ArgumentParser(
        prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='config file path')
    args = parser.parse_args()

    config = Config(log, args.configPath)
    # 打印banner信息
    utils = Utils(config)
    utils.info()

    init(config)
    sleep(3)
    login(config)
    sleep(1)
    watch(config)
    print(_("观看结束", color="green", lang=config.language))
    log.info(_log("观看结束", lang=config.language))


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sysQuit(driver, "Exit")
    except Exception as e:
        sysQuit(driver, format_exc())
