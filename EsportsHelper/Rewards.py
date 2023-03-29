import time
import traceback

import requests
from rich import print
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from EsportsHelper.util import DebugScreen


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
            time.sleep(10)
            DebugScreen(self.driver, "checkNewDrops", self.config.debug)

            isDrop = False
            imgUrl = []
            title = []
            imgEl = self.driver.find_elements(by=By.CSS_SELECTOR, value="img[class=img]")
            if len(imgEl) > 0:
                for img in imgEl:
                    imgUrl.append(img.get_attribute("src"))
                isDrop = True
            titleEl = self.driver.find_elements(by=By.CSS_SELECTOR, value="div[class=title]")
            if len(titleEl) > 0:
                for tit in titleEl:
                    title.append(tit.text)
                isDrop = True
            self.driver.implicitly_wait(15)
            if isDrop:
                return isDrop, imgUrl, title
            else:
                return isDrop, [], []
        except Exception:
            self.log.error("〒.〒 检查掉落失败")
            traceback.print_exc()
            print("[red]〒.〒 检查掉落失败[/red]")
            return False, [], []

    def notifyDrops(self, imgUrl, title):
        try:
            for i in range(len(imgUrl)):
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Drop掉落提醒",
                            "title": f"[{self.config.username}]{title[i]}",
                            "picUrl": f"{imgUrl[i]}",
                            "messageUrl": "https://lolesports.com/rewards"
                        }
                    }
                    requests.post(self.config.connectorDropsUrl, json=data)
                    time.sleep(5)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    embed = {
                        "title": "掉落提醒",
                        "description": f"[{self.config.username}]{title[i]}",
                        "image": {"url": f"{imgUrl[i]}"},
                        "thumbnail": {"url": "https://www.cdnjson.com/images/2023/03/26/QQ20230326153220.jpg"},
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    requests.post(self.config.connectorDropsUrl, headers={
                                  "Content-type": "application/json"}, json=params)
                    time.sleep(5)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"[{self.config.username}]{title[i]}"
                    }
                    requests.post(self.config.connectorDropsUrl, headers={
                                  "Content-type": "application/json"}, json=params)
                    time.sleep(5)
        except Exception:
            self.log.error("〒.〒 掉落提醒失败")
            traceback.print_exc()
            print("[red]〒.〒 掉落提醒失败[/red]")
