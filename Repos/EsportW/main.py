import argparse
from time import sleep
from traceback import format_exc, print_exc

from config import Config
from EsportsHelper.Config import Config
from EsportsHelper.Logger import log
from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.Match import Match
from EsportsHelper.Utils import info, sysQuit, print_green, print_red
from EsportsHelper.Webdriver import Webdriver
from match import Match
from rich import print
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


global driver

def watch(config):
    global driver
    try:
        driver = Webdriver(config).createWebdriver()
    except TypeError:
        print_exc()
        print_red("Error: Webdriver generation failure!\nCan't find the latest version of Google browser! If you haven't downloaded it or not the latest version, please check again and try again\nIf you have checked above, if you don’t check the node or try it, you can open it with an administrator\nExit by pressing any key...")
        input()
        sysQuit(driver, format_exc())
    except Exception as e:
        print_exc()
        print_red("Error: Webdriver generation failure!\nIs there a Google browser?\nIs it a network problem? Please check whether the VPN node is available\nExit by pressing any key...")
        input()
        sysQuit(driver, format_exc())

    loginHandler = LoginHandler(log=log, driver=driver)
    try:
        driver.get("https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")

    except Exception as e:
        driver.get("https://lolesports.com/schedule")
    driver.set_window_size(960, 768)
    
    tryLoginTimes = 4
    while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
        try:
            loginHandler.automaticLogIn(config.username, config.password)
        except TimeoutException:
            tryLoginTimes -= 1
            if tryLoginTimes <= 0:
                sysQuit(driver, "Unable to log in, wrong credentials or there is a problem with the network")
            print_red("Error: Automatic login fails, check the network and account password")

            sleep(5)
            print_red("Start cancelled")
            sysQuit(driver, "Automatic login fails")
    print_green("Logged in succesfully")

    Match(log=log, driver=driver, config=config).watchMatches(
        delay=config.delay, maxRunHours=config.maxRunHours)


def main():

    info()

    parser = argparse.ArgumentParser(
        prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='config file path')
    args = parser.parse_args()

    config = Config(log, args.configPath)

    watch(config)
    
 
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        sysQuit(driver, "The program is interrupted")
    except Exception as e:
        sysQuit(driver, format_exc())
