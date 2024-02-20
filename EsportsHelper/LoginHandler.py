from datetime import datetime
import time
import random
from time import sleep
from traceback import format_exc
from EsportsHelper.Config import config
from EsportsHelper.Stats import stats
from EsportsHelper.Utils import getLolesportsWeb, sysQuit, formatExc, debugScreen
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
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)
        self.quickWait = WebDriverWait(self.driver, 8)
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
                log.error(_log("无法打开Lolesports网页，网络问题"))
                log.error(formatExc(format_exc()))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('无法打开Lolesports网页，网络问题', 'red')}")
            sleep(2)
            loginButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
            self.driver.execute_script("arguments[0].click();", loginButton)
            log.info(f'<{config.nickName}> {_log("登录中...")}')
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
                (By.CSS_SELECTOR, "button[data-testid='btn-signin-submit']")))  # Sometimes the button was not pressed correctly, this is a possible fix
            sleep(1)
            self.driver.execute_script("arguments[0].click();", submitButton)
            log.info(_log("账密 提交成功"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('账密 提交成功', 'yellow')}")
            sleep(4)
            if len(self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text__web-code")) > 0:
                self.insert2FACode()
            try:
                self.quickWait.until(ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[data-testid='btn-signin-submit']")))
            except TimeoutException:
                log.info(_log("请前往浏览器手动解决验证码"))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('请前往浏览器手动解决验证码', 'yellow')}")
                if config.headless:
                    log.info(_log("headless情况下解决方案一: \n打开任意浏览器,在地址栏输入:") +
                             " chrome://inspect/#devices" +
                             _log("回车后等待一会,直到界面下方刷新出Remote Target,并点击对应登录界面的inspect,从而唤出调试用的浏览器界面,") +
                             _log("手动解决验证码后关闭之前弹出的界面即可."))
                    log.info(_log("解决方案二:\n请配置userDataDir来实现跳过验证码, 具体请查看github的wiki教程"))
                    stats.info.append(_("headless情况下解决方案一: \n打开任意浏览器,在地址栏输入:", color="yellow") +
                                      " [yellow]chrome://inspect/#devices[/]" +
                                      _("回车后等待一会,直到界面下方刷新出Remote Target,并点击对应登录界面的inspect,从而唤出调试用的浏览器界面,", color="yellow") +
                                      _("手动解决验证码后关闭之前弹出的界面即可.", color="yellow"))
                    stats.info.append(_("解决方案二:\n请配置userDataDir来实现跳过验证码, 具体请查看github的wiki教程", "yellow"))
                try:
                    WebDriverWait(self.driver, 110).until(ec.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.riotbar-summoner-name")))
                except TimeoutException:
                    debugScreen(self.driver, "LoginHandler")
                    log.error(_log("验证超时 请重新打开本脚本重试"))
                    stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('验证超时 请重新打开本脚本重试', 'red')}")
                    log.error(formatExc(format_exc()))
                    return False
                return True
            self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.riotbar-summoner-name")))
            return True
        except TimeoutException:
            debugScreen(self.driver, "LoginHandler")
            wait = WebDriverWait(self.driver, 7)
            try:
                blockInfo = wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "h1[data-translate=block_headline]")))
                if blockInfo.text == "Sorry, you have been blocked":
                    log.error(_log("当前网络环境被封锁,请更换网络环境"))
                    stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('当前网络环境被封锁,请更换网络环境', 'red')}")
                    log.error(formatExc(format_exc()))
                    return False
                errorInfo = wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.status-message.text__web-error > a")))
            except TimeoutException:
                log.error(_log("登录超时,检查网络或窗口是否被覆盖"))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('登录超时,检查网络或窗口是否被覆盖', 'red')}")
                log.error(formatExc(format_exc()))
                return False

            if errorInfo.text == "can't sign in":
                log.error(_log("登录失败,检查账号密码是否正确"))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('登录失败,检查账号密码是否正确', 'red')}")
            else:
                log.error(_log("登录超时,检查网络或窗口是否被覆盖"))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('登录超时,检查网络或窗口是否被覆盖', 'red')}")
            log.error(_log("登录失败"))
            log.error(formatExc(format_exc()))
            return False

    def insert2FACode(self) -> None:
        """
        Prompts the user to enter their two-factor authentication code, enters the code into the appropriate field,
        and submits the code.
        """
        authText = self.wait.until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "h5.grid-panel__subtitle")))
        log.info(f'{_log("请输入二级验证代码:")} ({authText.text})')
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
        log.info(_log("二级验证代码提交成功"))
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
            try:
                blockInfo = WebDriverWait(self.driver, 7).until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "h1[data-translate=block_headline]")))
                if blockInfo.text == "Sorry, you have been blocked":
                    log.error(_log("当前网络环境被封锁,请更换网络环境"))
                    stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('当前网络环境被封锁,请更换网络环境', 'red')}")
                    sleep(4)
                    sysQuit(self.driver, _log("当前网络环境被封锁,请更换网络环境"))
            except TimeoutException:
                pass
            try:
                WebDriverWait(self.driver, 7).until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[name=username]")))
                log.error(_log('免密登录失败,请去谷歌浏览器手动登录并勾选保持登录后再行尝试'))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('免密登录失败,请去谷歌浏览器手动登录并勾选保持登录后再行尝试', 'red')}")
                sleep(4)
                sysQuit(self.driver, _log('免密登录失败,请去谷歌浏览器手动登录并勾选保持登录后再行尝试'))
            except Exception:
                pass
        except TimeoutException:
            if self.driver.find_element(By.CSS_SELECTOR, "div.riotbar-summoner-name"):
                return
            debugScreen(self.driver, "userDataLogin")
            stats.status = _("登录失败", color="red")
            log.error(_log('免密登录失败,请去谷歌浏览器手动登录并勾选保持登录后再行尝试'))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('免密登录失败,请去谷歌浏览器手动登录并勾选保持登录后再行尝试', 'red')}")
            log.error(formatExc(format_exc()))
            sleep(4)
            sysQuit(self.driver, _log('免密登录失败,请去谷歌浏览器手动登录并勾选保持登录后再行尝试'))
