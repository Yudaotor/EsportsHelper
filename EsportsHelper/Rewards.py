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

    def findRewardsCheckmark(self):
        wait = WebDriverWait(self.driver, 15)
        try:
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div[class=status-summary] g")))
        except TimeoutException:
            return False
        return True

    def checkRewards(self, url, retries=4):
        splitUrl = url.split('/')
        if splitUrl[-2] != "live":
            match = splitUrl[-2]
        else:
            match = splitUrl[-1]
        for i in range(retries):
            if self.findRewardsCheckmark():
                self.log.info(f"{match} 可以正常观看 √√√√√ ")
                print(f"{match} 可以正常观看 [green]√√√√√ ")
                break
            else:
                if i < 3:
                    self.log.warning(f"{match} 观看异常 ××××× 重试中...")
                    print(f"{match} 观看异常 [yellow]××××× 重试中...")
                    self.driver.refresh()
                else:
                    self.log.error(f"{match} 观看异常 ××××× ")
                    print(f"{match} 观看异常 [red]××××× ")

    def checkNewDrops(self):
        self.driver.implicitly_wait(5)
        isDrop = False
        imgUrl = []
        title = []
        imgEl = self.driver.find_elements(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[1]/img")
        if len(imgEl) > 0:
            for img in imgEl:
                imgUrl.append(img.get_attribute("src"))
            isDrop = True
        titleEl = self.driver.find_elements(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div[2]")
        if len(titleEl) > 0:
            for tit in titleEl:
                title.append(tit.text)
            isDrop = True
        closeButton = self.driver.find_elements(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[3]/button[1]")
        time.sleep(1)
        if len(closeButton) > 0:
            for i in range(len(closeButton) - 1, -1, -1):
                closeButton[i].click()
        self.driver.implicitly_wait(15)
        if isDrop:
            return isDrop, imgUrl, title
        else:
            return isDrop, [], []

    def notifyDrops(self, imgUrl, title):
        try:
            for i in range(len(imgUrl)):
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Drop掉落提醒",
                            "title": f"{title[i]}",
                            "picUrl": f"{imgUrl[i]}",
                            "messageUrl": "https://lolesports.com/rewards"
                        }
                    }
                    requests.post(self.config.connectorDropsUrl, json=data)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    embed = {
                        "title": "掉落提醒",
                        "description": f"{title[i]}",
                        "image": {"url": f"{imgUrl[i]}"},
                        "thumbnail": {"url": f"{imgUrl[i]}"},
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    requests.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"{title[i]}",
                    }
                    requests.post(self.config.connectorDropsUrl, headers={"Content-type": "application/json"}, json=params)
        except Exception:
            self.log.error("掉落提醒失败")
            traceback.print_exc()
            print("[red]掉落提醒失败[/red]")
