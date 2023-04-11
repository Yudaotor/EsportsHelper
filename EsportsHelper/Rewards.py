import time
from traceback import format_exc
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from rich import print

from EsportsHelper.Utils import getMatchName


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
        for i in range(retryTimes):
            if self.isRewardMarkExist():
                self.log.info(f"√√√√√ {match} 正常观看 可获取奖励 √√√√√ ")
                print(f"[green]√√√√√[/green] {match} 正常观看 可获取奖励 [green]√√√√√ ")
                return True
            else:
                if i != retryTimes - 1:
                    self.log.warning(f"××××× {match} 观看异常 ××××× 重试中...")
                    print(
                        f"[yellow]×××××[/yellow] {match} 观看异常 [yellow]××××× 重试中...")
                    self.driver.refresh()
                    if stream == "youtube":
                        self.youtube.playYoutubeStream()
                else:
                    self.log.error(f"××××× {match} 观看异常 ××××× url={url}")
                    print(f"[red]×××××[/red] {match} 观看异常 [red]××××× url={url}")
                    self.utils.errorNotify(f"××××× {match} 观看异常 ×××××")
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
            drops = self.driver.find_elements(by=By.CSS_SELECTOR, value="div.InformNotifications > div > div.product-image > img")
            if len(drops) > 0:
                for i in range(len(drops)):
                    isDrop = True
                    self.utils.debugScreen(self.driver, "点击掉落前")
                    drops[i].click()
                    time.sleep(3)
                    self.utils.debugScreen(self.driver, "点击掉落后")
                    poweredByImg.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=presented-by] > img[class=img]").get_attribute("src"))
                    productImg.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=product-image] > img[class=img]").get_attribute("src"))
                    eventTitle.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div.RewardsDropsCard > div > div.title.short").text)
                    dropItem.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=reward] > div[class=wrapper] > div[class=title]").text)
                    unlockedDate.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div.RewardsDropsCard > div > div.unlocked-date").text)
                    dropItemImg.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=reward] > div[class=image] > img[class=img]").get_attribute("src"))
                    closeButton = self.driver.find_element(by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.close")
                    closeButton.click()
            if isDrop:
                self.driver.implicitly_wait(15)
                return isDrop, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg
            else:
                self.driver.implicitly_wait(15)
                return isDrop, [], [], [], [], [], []
        except Exception:
            self.driver.implicitly_wait(15)
            self.log.error("〒.〒 检查掉落失败")
            self.log.error(format_exc())
            print("[red]〒.〒 检查掉落失败[/red]")
            return False, [], [], [], [], [], []

    def notifyDrops(self, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg):
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
                    "title": "掉落提醒",
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
                s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                time.sleep(5)
            elif "https://fwalert.com" in self.config.connectorDropsUrl:
                params = {
                    "text": f"[{self.config.username}]通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                }
                s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                time.sleep(5)
            else:
                params = {
                    "text": f"[{self.config.username}]通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                }
                s.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                time.sleep(5)
            self.log.info(">_< 掉落提醒成功")
        except Exception:
            self.log.error("〒.〒 掉落提醒失败")
            self.log.error(format_exc())
            print("[red]〒.〒 掉落提醒失败[/red]")
