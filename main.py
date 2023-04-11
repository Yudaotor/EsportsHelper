import argparse
from selenium.common.exceptions import TimeoutException
from traceback import format_exc
from selenium.webdriver.common.by import By
from time import sleep

from rich import print
from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.Webdriver import Webdriver
from EsportsHelper.Logger import log
from EsportsHelper.Config import Config
from EsportsHelper.Match import Match
from EsportsHelper.Utils import info, sysQuit

global driver


def init(config):
    global driver
    # 生成webdriver
    try:
        driver = Webdriver(config).createWebdriver()
    except TypeError:
        print(
            "[red]눈_눈 生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开")
        input("按任意键退出...")
        sysQuit(driver, format_exc())
    except Exception:
        print("[red]눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用")
        input("按任意键退出...")
        sysQuit(driver, format_exc())
    # 设置窗口大小
    driver.set_window_size(960, 768)
    # 打开观赛页面
    try:
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
    except Exception:
        print("[red]눈_눈 无法打开网页!\n请检查网络是否正常,将于60秒后重试")
        log.error("无法打开网页!\n请检查网络是否正常,将于60秒后重试")
        sleep(60)
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
    # 切换语言到英语
    try:
        driver.find_element(
            by=By.CSS_SELECTOR, value="#riotbar-right-content > div._1K9T69nrXajaz_b4HNuhtI.riotbar-locale-switcher > div > a").click()
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
    sleep(2)
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
