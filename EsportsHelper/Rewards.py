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

    def isRewardMarkExist(self):
        wait = WebDriverWait(self.driver, 25)
        try:
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class=status-summary] g")))
        except TimeoutException:
            return False
        return True

    def checkRewards(self, stream, url, retryTimes=6) -> bool:
        match = getMatchName(url)
        teams = ""
        for i in range(retryTimes):
            if self.isRewardMarkExist():
                try:
                    if stream == "twitch":
                        wait = WebDriverWait(self.driver, 15)
                        wait.until(ec.frame_to_be_available_and_switch_to_it(
                            (By.CSS_SELECTOR, "iframe[title=Twitch]")))
                        teams = wait.until(ec.presence_of_element_located(
                            (By.CSS_SELECTOR, "div.Layout-sc-1xcs6mc-0.bZVrjx.tw-card-body > div > p:nth-child(2)"))).text
                        self.driver.switch_to.default_content()
                    elif stream == "youtube":
                        teams = self.driver.find_element(
                            By.CSS_SELECTOR, "iframe[id=video-player-youtube]").get_attribute("title")
                    if teams != "" and "|" in teams:
                        words = teams.split("|")
                        for word in words:
                            if "vs" in word.lower():
                                teams = word
                                break
                            else:
                                teams = words[0]
                    elif teams != "" and "-" in teams:
                        words = teams.split("-")
                        for word in words:
                            if "vs" in word.lower():
                                teams = word
                                break
                            else:
                                teams = words[0]
                    else:
                        teams = ""
                except Exception:
                    self.log.error(format_exc())
                self.log.info(
                    f"{match} {_log('正常观看 可获取奖励', lang=self.config.language)} {teams}")
                print(
                    f"{match} {_('正常观看 可获取奖励', color='green', lang=self.config.language)} {teams}")

                return True
            else:
                if i != retryTimes - 1:
                    self.log.warning(
                        f"{match} {_log('观看异常 重试中...', self.config.language)}")
                    print(
                        f"{match} {_('观看异常 重试中...', color='yellow', lang=self.config.language)}")
                    self.driver.refresh()
                    if stream == "youtube":
                        self.youtube.playYoutubeStream()
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
            isDrop = False
            poweredByImg = []
            productImg = []
            eventTitle = []
            dropItem = []
            dropItemImg = []
            unlockedDate = []
            drops = self.driver.find_elements(
                by=By.CSS_SELECTOR, value="div.InformNotifications > div > div.product-image > img")
            if len(drops) > 0:
                for i in range(len(drops)):
                    isDrop = True
                    drops[i].click()
                    poweredByImg.append(self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div[class=presented-by] > img[class=img]").get_attribute("src"))
                    productImg.append(self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div[class=product-image] > img[class=img]").get_attribute("src"))
                    try:
                        eventTitle.append(self.driver.find_element(
                            by=By.CSS_SELECTOR, value="div.RewardsDropsCard > div > div.title.short").text)
                    except Exception:
                        eventTitle.append(self.driver.find_element(
                            by=By.CSS_SELECTOR, value="div.RewardsDropsCard > div > div.title.long").text)
                    dropItem.append(self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div[class=reward] > div[class=wrapper] > div[class=title]").text)
                    unlockedDate.append(self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div.RewardsDropsCard > div > div.unlocked-date").text)
                    dropItemImg.append(self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div[class=reward] > div[class=image] > img[class=img]").get_attribute("src"))
                    closeButton = self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.close")
                    closeButton.click()
            if isDrop:
                self.driver.implicitly_wait(15)
                return isDrop, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg
            else:
                self.driver.implicitly_wait(15)
                return isDrop, [], [], [], [], [], []
        except Exception:
            self.driver.implicitly_wait(15)
            self.log.error(_log("检查掉落失败", lang=self.config.language))
            self.log.error(format_exc())
            print(_("检查掉落失败", color="red", lang=self.config.language))
            return False, [], [], [], [], [], []

    def notifyDrops(self, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg):
        if self.config.notifyType == "all" or self.config.notifyType == "drops":
            try:
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Drop掉落提醒",
                            "title": f"[{self.config.username}]通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                            "picUrl": f"{dropItemImg}",
                            "messageUrl": "https://lolesports.com/rewards"
                        }
                    }
                    s.post(self.config.connectorDropsUrl, json=data)
                    time.sleep(5)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
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
                        "name": "Unlocked-Date",
                        "value": f"{unlockedDate}",
                        "inline": True
                    }
                    fieldNone = {
                        "name": "",
                        "value": "",
                        "inline": True
                    }
                    embed = {
                        "title": "Drop!",
                        "description": f"{self.config.username}",
                        "image": {"url": f"{productImg}"},
                        "thumbnail": {"url": f"{dropItemImg}"},
                        "fields": [field1, field2, fieldNone, field4, fieldNone, fieldNone],
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
                        "text": f"[{self.config.username}]通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                    time.sleep(5)
                else:
                    params = {
                        "text": f"[{self.config.username}]通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                    time.sleep(5)
                self.log.info(_log("掉落提醒成功", lang=self.config.language))
            except Exception:
                self.log.error(_log("掉落提醒失败", lang=self.config.language))
                self.log.error(format_exc())
                print(_("掉落提醒失败", color="red", lang=self.config.language))
