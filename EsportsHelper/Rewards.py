import time
import traceback
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from rich import print


class Rewards:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config

    def isRewardMarkExist(self):
        wait = WebDriverWait(self.driver, 25)
        try:
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class=status-summary] g")))
        except TimeoutException:
            return False
        return True

    def checkRewards(self, url, retryTimes=6) -> bool:
        splitUrl = url.split('/')
        if splitUrl[-2] != "live":
            match = splitUrl[-2]
        else:
            match = splitUrl[-1]
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
                else:
                    self.log.error(f"××××× {match} 观看异常 ××××× url={url}")
                    print(f"[red]×××××[/red] {match} 观看异常 [red]××××× url={url}")
                    return False

    def checkNewDrops(self):
        try:
            self.driver.implicitly_wait(15)

            isDrop = False
            poweredByImg = []
            productImg = []
            unlockedDate = []
            eventTitle = []
            dropItem = []
            dropItemImg = []
            drops = self.driver.find_elements(by=By.CSS_SELECTOR, value="div[class=drops-fulfilled]")
            for drop in drops:
                isDrop = True
                drop.click()
                time.sleep(2)
                poweredByImg.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=sponsor-image] > img[class=img]"))
                productImg.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=product-image] > img[class=img]"))
                unlockedDate.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=product-image] > div[class=unlocked-date]"))
                eventTitle.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=product-image] > div[class=title]"))
                dropItem.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=reward] > div[class=wrapper] > div[class=title]"))
                dropItemImg.append(self.driver.find_element(by=By.CSS_SELECTOR, value="div[class=reward] > div[class=image] > img[class=img]"))
                self.driver.refresh()
            if isDrop:
                self.driver.implicitly_wait(15)
                return isDrop, poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg
            else:
                self.driver.implicitly_wait(15)
                return isDrop, [], [], [], [], [], []
        except Exception:
            self.driver.implicitly_wait(15)
            self.log.error("〒.〒 检查掉落失败")
            traceback.print_exc()
            print("[red]〒.〒 检查掉落失败[/red]")
            return False, [], [], [], [], [], []

    def notifyDrops(self, poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg):
        try:
            for i in range(len(poweredByImg)):
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Drop掉落提醒",
                            "title": f"[{self.config.username}]通过事件{eventTitle[i]} 获得{dropItem[i]} {unlockedDate[i]}",
                            "picUrl": f"{dropItemImg[i]}",
                            "messageUrl": "https://lolesports.com/rewards"
                        }
                    }
                    requests.post(self.config.connectorDropsUrl, json=data)
                    time.sleep(5)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    embed = {
                        "title": "掉落提醒",
                        "description": f"[{self.config.username}]通过事件{eventTitle[i]} 获得{dropItem[i]} {unlockedDate[i]}",
                        "image": {"url": f"{productImg[i]}"},
                        "thumbnail": {"url": f"{dropItemImg}"},
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    requests.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                    time.sleep(5)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"[{self.config.username}]通过事件{eventTitle[i]} 获得{dropItem[i]} {unlockedDate[i]}",
                    }
                    requests.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                    time.sleep(5)
                else:
                    params = {
                        "text": f"[{self.config.username}]通过事件{eventTitle[i]} 获得{dropItem[i]} {unlockedDate[i]}",
                    }
                    requests.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                    time.sleep(5)
        except Exception:
            self.log.error("〒.〒 掉落提醒失败")
            traceback.print_exc()
            print("[red]〒.〒 掉落提醒失败[/red]")
