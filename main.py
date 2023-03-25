import sys
import traceback
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import argparse
from rich import print
from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.VersionManager import VersionManager
from EsportsHelper.Webdriver import Webdriver
from EsportsHelper.Logger import Logger
from EsportsHelper.Config import Config
from EsportsHelper.Match import Match


CURRENT_VERSION = "1.0.0"


def info():
    print("[green]=========================================================")
    print(f"========        感谢使用 [blue]电竞助手 v{CURRENT_VERSION}[/blue]!        ========")
    print("============ 本程序开源于github链接地址如下: ============")
    print("====   https://github.com/Yudaotor/EsportsHelper     ====")
    print("==== 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! ====")
    print("[green]=========================================================")
    print()


def main():
    info()
    parser = argparse.ArgumentParser(prog='CapsuleFarmer.exe', description='Farm Esports Capsules by watching lolesports.com.')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='config file path')
    args = parser.parse_args()
    Path("./logs/").mkdir(parents=True, exist_ok=True)
    log = Logger().createLogger()
    config = Config(log, args.configPath)
    if not VersionManager.isLatestVersion(CURRENT_VERSION):
        log.warning("\n==!!! 新版本可用 !!!==\n ==请从此处下载: ==")
    print("[yellow]\n==!!! 新版本可用 !!!==\n ==请从此处下载: https://github.com/Yudaotor/EsportsHelper/releases/latest ==[/yellow]")
    driver = None
    try:
        driver = Webdriver(headless=config.headless).createWebdriver()
    except Exception as ex:
        traceback.print_exc()
        log.error(traceback.format_exc())
        print("[red]生成WEBDRIVER失败! 你是否使用的是最新版浏览器? 为你配置的浏览器检查一下更新吧\n按任意键退出...")
        input()
        exit()
    loginHandler = LoginHandler(log=log, driver=driver)
    driver.get("https://lolesports.com/schedule")
    try:
        loginHandler.automaticLogIn(config.username, config.password)
    except TimeoutException:
        log.error("自动登录失败,账号密码是否正确?")
        print("[red]自动登录失败,账号密码是否正确?[/red]")
        if config.headless:
            driver.quit()
            log.info("退出中...")
            print("[green]退出中...[/green]")
            exit()
    while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
        log.info("等待登录中...")
        print("[yellow]等待登录中...[/yellow]")
        time.sleep(5)
    log.info("好嘞 登录成功!")
    print("[green]好嘞 登录成功![/green]")
    Match(log=log, driver=driver, config=config).watchMatches(delay=config.delay)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("[red]------程序退出------")
        sys.exit()