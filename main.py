import argparse
from selenium.common.exceptions import TimeoutException, WebDriverException
from traceback import format_exc
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support import expected_conditions as ec
from rich import print
from selenium.webdriver.support.wait import WebDriverWait

from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.Webdriver import Webdriver
from EsportsHelper.Logger import log
from EsportsHelper.Config import Config
from EsportsHelper.Match import Match
from EsportsHelper.Utils import info, sysQuit, getLolesportsWeb

global driver


def init(config):
    global driver
    # 生成webdriver
    try:
        driver = Webdriver(config).createWebdriver()
    except TypeError:
        driver = None
        log.error(format_exc())
        print(
            "[red]눈_눈 生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开")
        input("按任意键退出...")
        sysQuit(driver)
    except WebDriverException:
        driver = None
        log.error(format_exc())
        print("[red]눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是否打开着谷歌浏览器?请关闭后再次尝试")
        input("按任意键退出...")
        sysQuit(driver)
    except Exception:
        driver = None
        log.error(format_exc())
        print("[red]눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用")
        input("按任意键退出...")
        sysQuit(driver)
    # 设置窗口大小
    driver.set_window_size(960, 768)
    # 打开观赛页面
    try:
        getLolesportsWeb(driver)
    except Exception:
        log.error(format_exc())
        log.error("Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...")
        print(f"[red]Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...[/red]")
        sysQuit(driver, "网络问题，将于3秒后退出...")
    # 切换语言到英语
    try:
        wait = WebDriverWait(driver, 20)
        languageButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#riotbar-right-content > div._1K9T69nrXajaz_b4HNuhtI.riotbar-locale-switcher > div > a")))
        languageButton.click()
        driver.find_element(by=By.CSS_SELECTOR,
                            value="#riotbar-right-content > div._1K9T69nrXajaz_b4HNuhtI.riotbar-locale-switcher > div._2iYBTCEu1pbDL1lBawLJ3O.locale-switcher-dropdown > ul > li:nth-child(1) > a").click()
        log.info("切换语言成功")
    except TimeoutException:
        log.error("눈_눈 切换语言失败")
        log.error(format_exc())
    except Exception:
        log.error("눈_눈 切换语言失败")
        log.error(format_exc())


def login(config):
    loginHandler = LoginHandler(log=log, driver=driver)
    if config.userDataDir == "":
        tryLoginTimes = 4
        while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
            try:
                loginHandler.automaticLogIn(config.username, config.password)
            except TimeoutException:
                tryLoginTimes = tryLoginTimes - 1
                if tryLoginTimes <= 0:
                    sysQuit(driver, "无法登陆，账号密码可能错误或者网络出现问题")

                log.error("눈_눈 自动登录失败,检查网络和账号密码")
                print("[red]눈_눈 自动登录失败,检查网络和账号密码[/red]")
                sleep(5)
                log.error("눈_눈 开始重试")

        log.info("∩_∩ 好嘞 登录成功")
        print("[green]∩_∩ 好嘞 登录成功[/green]")
    else:
        loginHandler.userDataLogin()
        log.info("∩_∩ 使用系统数据 自动登录成功")
        print("[green]∩_∩ 使用系统数据 自动登录成功[/green]")


def watch(config):
    Match(log=log, driver=driver, config=config).watchMatches(
        delay=config.delay, maxRunHours=config.maxRunHours)


def main():
    global driver
    # 打印banner信息
    info()
    # 解析配置参数
    parser = argparse.ArgumentParser(
        prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='config file path')
    args = parser.parse_args()

    config = Config(log, args.configPath)
    init(config)
    sleep(3)
    login(config)
    sleep(1)
    watch(config)
    print("[green]观看结束～[/green]")
    log.info("观看结束～")


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sysQuit(driver, "程序被打断")
    except Exception as e:
        sysQuit(driver, format_exc())
