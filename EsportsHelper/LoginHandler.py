import time
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from rich import print


class LoginHandler:
    def __init__(self, log, driver) -> None:
        self.log = log
        self.driver = driver

    def automaticLogIn(self, username, password):
        try:
            try:
                self.driver.get(
                    "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
            except Exception as e:
                self.driver.get("https://lolesports.com/schedule")
            time.sleep(2)
            loginButton = self.driver.find_element(by=By.CSS_SELECTOR, value="a[data-riotbar-link-id=login]")
            self.driver.execute_script("arguments[0].click();", loginButton)
            self.log.info("눈_눈 登录中...")
            print("[yellow]눈_눈 登录中...")
            time.sleep(2)
            wait = WebDriverWait(self.driver, 15)
            usernameInput = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "input[name=username]")))
            usernameInput.send_keys(username)
            time.sleep(1)
            passwordInput = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "input[name=password]")))
            passwordInput.send_keys(password)
            time.sleep(1)
            submitButton = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]")))
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", submitButton)
            self.log.debug("∩_∩ 账密 提交成功")
            print("[green]∩_∩ 账密 提交成功")
            time.sleep(5)
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.riotbar-summoner-name")))
        except Exception as e:
            traceback.print_exc()
            self.log.error(traceback.format_exc())

