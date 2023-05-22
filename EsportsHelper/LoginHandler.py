from time import sleep
from traceback import format_exc
from EsportsHelper.Config import config
from EsportsHelper.Utils import getLolesportsWeb, sysQuit
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
    def __init__(self, driver) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(self.driver, 20)

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
                self.log.error(format_exc())
                print(_("无法打开Lolesports网页，网络问题", color="red"))
            sleep(2)
            loginButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
            self.log.info(_log("登录中..."))
            print(_("登录中...", color="yellow"))
            sleep(2)
            usernameInput = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name=username]")))
            usernameInput.send_keys(username)
            sleep(1)
            passwordInput = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name=password]")))
            passwordInput.send_keys(password)
            sleep(1)
            submitButton = self.wait.until(ec.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[type=submit]")))
            sleep(1)
            self.driver.execute_script("arguments[0].click();", submitButton)
            self.log.info(_log("账密 提交成功"))
            print(f'--{_("账密 提交成功", color="yellow")}')
            sleep(4)
            if len(self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text__web-code")) > 0:
                self.insert2FACode()
            self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.riotbar-summoner-name")))
            return True
        except TimeoutException:
            wait = WebDriverWait(self.driver, 7)
            errorInfo = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "span.status-message.text__web-error > a")))
            if errorInfo.text == "can't sign in":
                self.log.error(_log("登录失败,检查账号密码是否正确"))
                print(f'--{_("登录失败,检查账号密码是否正确", color="red")}')
            else:
                print(f'--{_("登录超时,检查网络或窗口是否被覆盖", color="red")}')
                self.log.error(_log("登录超时,检查网络或窗口是否被覆盖"))
            self.log.error(format_exc())
            return False

    def insert2FACode(self) -> None:
        """
        Prompts the user to enter their two-factor authentication code, enters the code into the appropriate field,
        and submits the code.
        """
        authText = self.wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "h5.grid-panel__subtitle")))
        self.log.info(f'{_log("请输入二级验证代码:")} ({authText.text})')
        code = input(_log("请输入二级验证代码:"))
        codeInput = self.wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "div.codefield__code--empty > div > input")))
        codeInput.send_keys(code)
        submitButton = self.wait.until(ec.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type=submit]")))
        self.driver.execute_script("arguments[0].click();", submitButton)
        self.log.info(_log("二级验证代码提交成功"))

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
            if self.driver.find_element(By.CSS_SELECTOR, "div.riotbar-summoner-name"):
                return
            print(f'--{_("免密登录失败,请去浏览器手动登录后再行尝试", color="red")}')
            self.log.error(_log("免密登录失败,请去浏览器手动登录后再行尝试"))
            self.log.error(format_exc())
            sysQuit(self.driver, _log("免密登录失败,请去浏览器手动登录后再行尝试"))
