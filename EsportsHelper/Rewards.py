import time
from traceback import format_exc

import requests
from EsportsHelper.Utils import _, _log, getMatchName
from rich import print
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class Rewards:
    def __init__(self, log, driver, config, youtube, utils) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.youtube = youtube
        self.utils = utils
        self.wait = WebDriverWait(self.driver, 25)

    def isRewardMarkExist(self):
        try:
            self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class=status-summary] g")))
        except TimeoutException:
            return False
        return True

    def checkRewards(self, stream, url, retryTimes=6) -> bool:
        match = getMatchName(url)
        teams = ""
        peopleNumber = ""
        for i in range(retryTimes):
            if self.isRewardMarkExist():
                try:
                    if stream == "twitch":
                        frameLocator = (By.CSS_SELECTOR, "iframe[title=Twitch]")
                        self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))

                        teamLocator = (By.CSS_SELECTOR, "p[data-test-selector=stream-info-card-component__subtitle]")
                        teams = self.wait.until(ec.presence_of_element_located(teamLocator)).text

                        peopleLocator = (By.CSS_SELECTOR, "p[data-test-selector=stream-info-card-component__description]")
                        peopleInfo = self.wait.until(ec.presence_of_element_located(peopleLocator)).text
                        for num in peopleInfo:
                            if num.isdigit():
                                peopleNumber += num
                        self.driver.switch_to.default_content()
                    elif stream == "youtube":
                        frameLocator = (By.ID, "video-player-youtube")
                        self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))
                        iframeTitle = self.driver.execute_script("return document.title;")
                        teams = iframeTitle.strip() if iframeTitle else ""
                        self.driver.switch_to.default_content()
                    if teams and ("|" in teams or "-" in teams):
                        delimiter = "|" if "|" in teams else "-"
                        words = teams.split(delimiter)
                        for word in words:
                            if "vs" in word.lower():
                                teams = word
                                break
                            else:
                                teams = words[0]
                    else:
                        teams = ""
                except Exception:
                    self.driver.switch_to.default_content()
                    self.log.error(format_exc())
                if stream == "twitch":
                    self.log.info(
                        f"{match} {_log('正常观看 可获取奖励', lang=self.config.language)} "
                        f"{teams} {peopleNumber} {_log('人观看', lang=self.config.language)}")
                    print(
                        f"{match} {_('正常观看 可获取奖励', color='green', lang=self.config.language)} "
                        f"{teams} {peopleNumber} {_('人观看', color='green', lang=self.config.language)}")
                elif stream == "youtube":
                    self.log.info(
                        f"{match} {_log('正常观看 可获取奖励', lang=self.config.language)} "
                        f"{teams}")
                    print(
                        f"{match} {_('正常观看 可获取奖励', color='green', lang=self.config.language)} "
                        f"{teams}")

                return True
            else:
                if i != retryTimes - 1:
                    self.log.warning(
                        f"{match} {_log('观看异常 重试中...', self.config.language)}")
                    print(
                        f"{match} {_('观看异常 重试中...', color='yellow', lang=self.config.language)}")
                    self.driver.refresh()
                    if stream == "youtube":
                        self.youtube.checkYoutubeStream()
                else:
                    self.log.error(
                        f"{match} {_log('观看异常', lang=self.config.language)}")
                    print(
                        f"{match} {_('观看异常', color='red', lang=self.config.language)}")
                    self.utils.errorNotify(
                        f"{match} {_log('观看异常', lang=self.config.language)}")
                    return False

    def checkNewDrops(self):
        try:
            self.driver.implicitly_wait(5)
            wait = WebDriverWait(self.driver, 10)
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div[class=product-image] > img[class=img]")))
            poweredByImg = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div[class=sponsor-image] > img[class=img]").get_attribute("src")
            productImg = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div[class=product-image] > img[class=img]").get_attribute("src")
            try:
                eventTitle = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div.title.short").text
            except Exception:
                eventTitle = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div.title.long").text
            dropItem = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div[class=reward] > div[class=wrapper] > div[class=title]").text
            unlockedDate = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div.unlocked-date").text
            dropItemImg = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div[class=reward] > div[class=image] > img[class=img]").get_attribute("src")
            closeButton = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.close")
            closeButton.click()
            self.driver.implicitly_wait(15)
            return poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg
        except Exception:
            self.driver.implicitly_wait(15)
            self.log.error(_log("检查掉落失败", lang=self.config.language))
            self.log.error(format_exc())
            print(_("检查掉落失败", color="red", lang=self.config.language))
            return None, None, None, None, None, None

    def notifyDrops(self, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg, dropLocale):
        if self.config.notifyType == "all" or self.config.notifyType == "drops":
            try:
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Drop掉落提醒",
                            "title": f"[{self.config.nickName}]在{dropLocale} 通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                            "picUrl": f"{dropItemImg}",
                            "messageUrl": "https://lolesports.com/rewards"
                        }
                    }
                    s.post(self.config.connectorDropsUrl, json=data)
                    time.sleep(5)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    field0 = {
                        "name": "Account",
                        "value": f"{self.config.nickName}",
                        "inline": True
                    }
                    field1 = {
                        "name": "Event",
                        "value": f"{eventTitle}",
                        "inline": True
                    }
                    field2 = {
                        "name": "Reward",
                        "value": f"{dropItem}",
                        "inline": True
                    }
                    field4 = {
                        "name": "Date",
                        "value": f"{unlockedDate}",
                        "inline": True
                    }
                    field5 = {
                        "name": "Locale",
                        "value": f"{dropLocale}",
                        "inline": True
                    }
                    fieldNone = {
                        "name": "",
                        "value": "",
                        "inline": True
                    }
                    embed = {
                        "title": "Drop!",
                        "image": {"url": f"{productImg}"},
                        "thumbnail": {"url": f"{dropItemImg}"},
                        "fields": [field0, field1, fieldNone, field2, field4, field5, fieldNone],
                        "color": 6676471,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                    time.sleep(5)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"[{self.config.nickName}]在{dropLocale} 通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                    time.sleep(5)
                else:
                    params = {
                        "text": f"[{self.config.nickName}]在{dropLocale} 通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                    time.sleep(5)
                self.log.info(_log("掉落提醒成功", lang=self.config.language))
            except Exception:
                self.log.error(_log("掉落提醒失败", lang=self.config.language))
                self.log.error(format_exc())
                print(_("掉落提醒失败", color="red", lang=self.config.language))
