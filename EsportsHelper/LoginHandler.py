import time
from traceback import format_exc
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from rich import print
from EsportsHelper.Utils import sysQuit
from EsportsHelper.Utils import getLolesportsWeb


class LoginHandler:
    def __init__(self, log, driver) -> None:
        self.log = log
        self.driver = driver

    def automaticLogIn(self, username, password):
        try:
            try:
                getLolesportsWeb(self.driver)
            except Exception:
                self.log.error(format_exc())
                self.log.error("Π——Π 无法打开Lolesports网页，网络问题")
                print(f"[red]Π——Π 无法打开Lolesports网页，网络问题[/red]")
            time.sleep(2)
            wait = WebDriverWait(self.driver, 11)
            loginButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
            self.log.info("눈_눈 登录中...")
            print("[yellow]눈_눈 登录中...")
            time.sleep(2)
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
            if len(self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text__web-code")) > 0:
                self.insert2FACode()
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.riotbar-summoner-name")))
        except TimeoutException:
            print("[red]×_× 网络问题 登录超时")
            self.log.error(format_exc())

    def insert2FACode(self):
        wait = WebDriverWait(self.driver, 20)
        authText = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "h5.grid-panel__subtitle")))
        self.log.info(f'输入二级验证代码 ({authText.text})')
        code = input('请输入二级验证代码: ')
        codeInput = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.codefield__code--empty > div > input")))
        codeInput.send_keys(code)
        submitButton = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]")))
        self.driver.execute_script("arguments[0].click();", submitButton)
        self.log.info("二级验证代码提交成功")

    def userDataLogin(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            loginButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
        except TimeoutException:
            if self.driver.find_element(By.CSS_SELECTOR, "div.riotbar-summoner-name"):
                return
            print("[red]×_× 免密登录失败,请去浏览器手动登录后再行尝试")
            self.log.error("免密登录失败,请去浏览器手动登录后再行尝试")
            self.log.error(format_exc())
            sysQuit(self.driver, "免密登录失败,请去浏览器手动登录后再行尝试")
