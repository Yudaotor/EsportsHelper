from datetime import datetime
import time
import random
from time import sleep
from traceback import format_exc
from EsportsHelper.Config import config
from EsportsHelper.Stats import stats
from EsportsHelper.Utils import getLolesportsWeb, sysQuit, Utils, formatExc
from rich import print
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from EsportsHelper.I18n import i18n
from EsportsHelper.Logger import log
_ = i18n.getText
_log = i18n.getLog


class LoginHandler:
    def __init__(self, driver, locks) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(self.driver, 20)
        self.locks = locks

    def automaticLogIn(self, username: str, password: str) -> bool:
        """
        An automatic login function that logs in with a given username and password.
        :param username: str，username
        :param password: str，password
        :return: bool True if login is successful, False if login is unsuccessful
        """
        try:
            try:
                getLolesportsWeb(self.driver)
            except Exception:
                self.log.error(_log("无法打开Lolesports网页，网络问题"))
                self.log.error(formatExc(format_exc()))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('无法打开Lolesports网页，网络问题', 'red')}")
            sleep(2)
            loginButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
            self.log.info(f'<{self.config.nickName}> {_log("登录中...")}')
            stats.status = _("登录中", color="yellow")
            sleep(2)
            usernameInput = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name=username]")))
            for character in username:
                usernameInput.send_keys(character)
                time.sleep(random.uniform(0.02, 0.1))  # wait a random time between 20 ms and 100 ms
            sleep(1)
            passwordInput = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name=password]")))
            for character in password:
                passwordInput.send_keys(character)
                time.sleep(random.uniform(0.02, 0.1))  # wait a random time between 20 ms and 100 ms
            sleep(1)
            submitButton = self.wait.until(ec.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='btn-signin-submit']"))) # Sometimes the button was not pressed correctly, this is a possible fix
            sleep(1)
            self.driver.execute_script("arguments[0].click();", submitButton)
            self.log.info(_log("账密 提交成功"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('账密 提交成功', 'yellow')}")
            sleep(4)
            if len(self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text__web-code")) > 0:
                self.insert2FACode()
            self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.riotbar-summoner-name")))
            return True
        except TimeoutException:
            Utils().debugScreen(self.driver, "LoginHandler")
            wait = WebDriverWait(self.driver, 7)
            errorInfo = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "span.status-message.text__web-error > a")))
            if errorInfo.text == "can't sign in":
                self.log.error(_log("登录失败,检查账号密码是否正确"))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('登录失败,检查账号密码是否正确', 'red')}")
            else:
                self.log.error(_log("登录超时,检查网络或窗口是否被覆盖"))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('登录超时,检查网络或窗口是否被覆盖', 'red')}")
            self.log.error(formatExc(format_exc()))
            return False

    def insert2FACode(self) -> None:
        """
        Prompts the user to enter their two-factor authentication code, enters the code into the appropriate field,
        and submits the code.
        """
        authText = self.wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "h5.grid-panel__subtitle")))
        self.log.info(f'{_log("请输入二级验证代码:")} ({authText.text})')
        stats.status = _("二级验证", color="yellow")
        sleep(3)
        self.locks["refreshLock"].acquire()
        code = input(_log("请输入二级验证代码:"))
        if self.locks["refreshLock"].locked():
            self.locks["refreshLock"].release()
        codeInput = self.wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "div.codefield__code--empty > div > input")))
        codeInput.send_keys(code)
        submitButton = self.wait.until(ec.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type=submit]")))
        self.driver.execute_script("arguments[0].click();", submitButton)
        self.log.info(_log("二级验证代码提交成功"))
        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('二级验证代码提交成功', 'green')}")

    def userDataLogin(self) -> None:
        """
        Attempt to log in using the user's stored credentials. If successful, return None.
        If unsuccessful, prompt the user to log in manually.

        :return: None
        """
        try:
            loginButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
        except TimeoutException:
            Utils().debugScreen(self.driver, "userDataLogin")
            if self.driver.find_element(By.CSS_SELECTOR, "div.riotbar-summoner-name"):
                return
            stats.status = _("登录失败", color="red")
            self.log.error(_log("免密登录失败,请去浏览器手动登录后再行尝试"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('免密登录失败,请去浏览器手动登录后再行尝试', 'red')}")
            self.log.error(formatExc(format_exc()))
            sysQuit(self.driver, _log("免密登录失败,请去浏览器手动登录后再行尝试"))
