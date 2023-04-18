import time
from traceback import format_exc

from EsportsHelper.Utils import _, _log, getLolesportsWeb, sysQuit
from rich import print
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class LoginHandler:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config

    def automaticLogIn(self, username, password):
        try:
            try:
                getLolesportsWeb(self.driver)
            except Exception:
                self.log.error(format_exc())
                self.log.error(_log("Π——Π 无法打开Lolesports网页，网络问题"),
                               lang=self.config.language)
                print(_("Π——Π 无法打开Lolesports网页，网络问题",
                      color="red", lang=self.config.language))
            time.sleep(2)
            wait = WebDriverWait(self.driver, 11)
            loginButton = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
            self.log.info(_log("눈_눈 登录中...", lang=self.config.language))
            print(_("눈_눈 登录中...", color="yellow", lang=self.config.language))
            time.sleep(2)
            usernameInput = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name=username]")))
            usernameInput.send_keys(username)
            time.sleep(1)
            passwordInput = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name=password]")))
            passwordInput.send_keys(password)
            time.sleep(1)
            submitButton = wait.until(ec.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[type=submit]")))
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", submitButton)
            self.log.info(_log("∩_∩ 账密 提交成功", lang=self.config.language))
            print(_("∩_∩ 账密 提交成功", color="green", lang=self.config.language))
            time.sleep(5)
            if len(self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text__web-code")) > 0:
                self.insert2FACode()
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.riotbar-summoner-name")))
        except TimeoutException:
            print(_("×_× 网络问题 登录超时", color="red", lang=self.config.language))
            self.log.error(_log("×_× 网络问题 登录超时", lang=self.config.language))
            self.log.error(format_exc())

    def insert2FACode(self):
        wait = WebDriverWait(self.driver, 20)
        authText = wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "h5.grid-panel__subtitle")))
        self.log.info(
            f'{_log("请输入二级验证代码:", lang=self.config.language)} ({authText.text})')
        code = input(_log("请输入二级验证代码:", lang=self.config.language))
        codeInput = wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "div.codefield__code--empty > div > input")))
        codeInput.send_keys(code)
        submitButton = wait.until(ec.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type=submit]")))
        self.driver.execute_script("arguments[0].click();", submitButton)
        self.log.info(_log("二级验证代码提交成功", lang=self.config.language))

    def userDataLogin(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            loginButton = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
        except TimeoutException:
            if self.driver.find_element(By.CSS_SELECTOR, "div.riotbar-summoner-name"):
                return
            print(_("免密登录失败,请去浏览器手动登录后再行尝试", color="red", lang=self.config.language))
            self.log.error(_log("免密登录失败,请去浏览器手动登录后再行尝试",
                           lang=self.config.language))
            self.log.error(format_exc())
            sysQuit(self.driver, _("免密登录失败,请去浏览器手动登录后再行尝试",
                    color="red", lang=self.config.language))
