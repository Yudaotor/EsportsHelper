from time import sleep
from traceback import format_exc, print_exc

from rich import print
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class Twitch:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log

    def setTwitchQuality(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(ec.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[title=Twitch]")))
            sleep(3)
            self.driver.implicitly_wait(15)
            isMute = self.driver.find_elements(By.CSS_SELECTOR, "button[data-a-target=player-mute-unmute-button] > div > div > div > svg > g")
            muteButton = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-mute-unmute-button]")))
            if len(isMute) <= 0:
                try:
                    muteButton.click()
                    self.log.info("Twitch: UnMute")
                    print("Twitch: UnMute")
                except Exception:
                    self.driver.execute_script("arguments[0].click();", muteButton)
                    print("Twitch: UnMute")
                    self.log.info("Twitch: UnMute")
            sleep(1)
            settingsButton = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-settings-button]")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            sleep(1)
            qualityButton = wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-settings-menu-item-quality]")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            sleep(1)
            options = wait.until(ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "input[data-a-target=tw-radio]")))
            self.driver.execute_script("arguments[0].click();", options[-1])
            sleep(1)
            self.driver.switch_to.default_content()
            return True
        except TimeoutException:
            self.log.error(format_exc())
            return False
        except Exception:
            self.log.error(format_exc())
            return False
