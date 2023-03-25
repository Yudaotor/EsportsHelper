from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


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
                self.log.info(f"{match} 有资格获取掉落 ✔ ")
                break
            else:
                if i < 3:
                    self.log.warning(f"{match} 没有资格获取掉落 ❌ 重试中...")
                    self.driver.refresh()
                else:
                    self.log.error(f"{match} 没有资格获取掉落 ❌ ")

