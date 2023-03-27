import time
import traceback
from rich import print
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


class Twitch:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log

    def setTwitchQuality(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title=Twitch]")))
            time.sleep(3)
            muteButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-mute-unmute-button]")))
            try:
                muteButton.click()
            except TimeoutError:
                self.driver.execute_script("arguments[0].click();", muteButton)
            time.sleep(1)
            settingsButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-settings-button]")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            time.sleep(1)
            qualityButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-settings-menu-item-quality]")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            time.sleep(1)
            options = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "input[data-a-target=tw-radio]")))
            self.driver.execute_script("arguments[0].click();", options[-1])
            time.sleep(1)
            self.driver.switch_to.default_content()
            return True
        except Exception as e:
            traceback.print_exc()
            self.log.error(traceback.format_exc())
            return False
