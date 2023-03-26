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

CURRENT_VERSION = "1.1.0"
global driver


def info():
    print("[green]=========================================================")
    print(f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{CURRENT_VERSION}!        [green]========[/green]")
    print("[green]============[/green] 本程序开源于github链接地址如下: [green]============[/green]")
    print("[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
    print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
    print("[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
    print("[green]====[/green] 如需关闭请勿直接右上角×关闭，请按Ctrl+C来关闭. [green]====[/green]")
    print("[green]=========================================================")
    print()


def main():
    global driver
    info()
    parser = argparse.ArgumentParser(prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='config file path')
    args = parser.parse_args()
    Path("./logs/").mkdir(parents=True, exist_ok=True)
    log = Logger().createLogger()
    config = Config(log, args.configPath)
    if not VersionManager.isLatestVersion(CURRENT_VERSION):
        log.warning("\n==!!! 新版本可用 !!!==\n ==请从此处下载: ==")
        print("[yellow]\n==!!! 新版本可用 !!!==\n ==请从此处下载: https://github.com/Yudaotor/EsportsHelper/releases/latest ==[/yellow]")
    try:
        driver = Webdriver(headless=config.headless).createWebdriver()
    except Exception as ex:
        traceback.print_exc()
        log.error(traceback.format_exc())
        print("[red](눈_눈) 生成WEBDRIVER失败!\n 你是否使用的是最新版谷歌浏览器? 网络是否没问题?\n为谷歌浏览器检查一下更新吧,或者说，去下一个？\n按任意键退出...")
        input()
        exit()
    loginHandler = LoginHandler(log=log, driver=driver)
    driver.get("https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
    try:
        loginHandler.automaticLogIn(config.username, config.password)
    except TimeoutException:
        log.error("(눈_눈) 自动登录失败,账号密码是否正确?")
        print("[red](눈_눈) 自动登录失败,账号密码是否正确?[/red]")
        if config.headless:
            driver.quit()
            log.info("退出中...")
            print("[green]退出中...[/green]")
            exit()
    while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
        print("[red](눈_눈) 自动登录失败...[/red]")
        log.error("(눈_눈) 自动登录失败...")
        log.info("(눈_눈) 等待登录中...")
        print("[yellow](눈_눈) 等待登录中...[/yellow]")
        time.sleep(5)
    log.info("(∩_∩) 好嘞 登录成功!ε=(´ο｀*)")
    print("[green](∩_∩) 好嘞 登录成功![/green]")
    Match(log=log, driver=driver, config=config).watchMatches(delay=config.delay)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        global driver
        driver.quit()
        print("[red]------程序退出------")
        sys.exit()
