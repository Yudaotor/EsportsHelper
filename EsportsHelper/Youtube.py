import time
import traceback

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

class Youtube:
    def __init__(self, driver) -> None:
        self.driver = driver

    def setYoutubeQuality(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[id=video-player-youtube]")))
            wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div/div/div[27]/div[2]/div[1]/button"))).click()

            # muteButton = wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[27]/div[2]/div[1]/span/button")))
            # self.driver.execute_script("arguments[0].click();", muteButton)
            time.sleep(1)
            settingsButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-tooltip-target-id=ytp-settings-button]")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            time.sleep(1)
            qualityButton = wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[25]/div/div/div[2]/div[3]")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            time.sleep(1)
            option = wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[25]/div/div[2]/div[6]/div")))
            self.driver.execute_script("arguments[0].click();", option)
            self.driver.switch_to.default_content()
        except Exception as e:
            traceback.print_exc()
