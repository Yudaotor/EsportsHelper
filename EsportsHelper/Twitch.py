from time import sleep
from traceback import format_exc

from rich import print
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class Twitch:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log
        self.wait = WebDriverWait(self.driver, 25)

    def setTwitchQuality(self) -> bool:
        """
        Sets the quality of the Twitch video player to the lowest available option and unmute the audio.

        Returns:
            True if the operation is successful, False otherwise.
        """
        try:
            self.wait.until(ec.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[title=Twitch]")))
            sleep(2)
            settingsButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-settings-button]")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            sleep(1)
            qualityButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-settings-menu-item-quality]")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            sleep(1)
            options = self.wait.until(ec.presence_of_all_elements_located(
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

    def checkTwitchStream(self) -> bool:
        try:
            self.wait.until(ec.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[title=Twitch]")))
            sleep(3)
            self.driver.implicitly_wait(15)
            isMute = self.driver.find_elements(By.CSS_SELECTOR, "button[data-a-target=player-mute-unmute-button] > div > div > div > svg > g")
            muteButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-mute-unmute-button]")))
            if len(isMute) <= 0:
                self.unmuteStream(muteButton)
            playButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-play-pause-button]")))
            if playButton.get_attribute("data-a-player-state") == "paused":
                self.playStream(playButton)
            self.driver.switch_to.default_content()
            return True
        except TimeoutException:
            self.log.error(format_exc())
            self.driver.switch_to.default_content()
            return False
        except Exception:
            self.log.error(format_exc())
            self.driver.switch_to.default_content()
            return False

    def unmuteStream(self, muteButton):
        """
        Unmute the stream by clicking the given mute button. If the click fails,
        executes a JavaScript click to try again. Also prints a message to the console
        and logs the action to the application log.

        Args:
            muteButton (WebElement): The mute button element to click.

        Returns:
            None
        """
        try:
            muteButton.click()
            print("Twitch: UnMute")
            self.log.info("Twitch: UnMute")
        except Exception:
            self.driver.execute_script("arguments[0].click();", muteButton)
            print("Twitch: UnMute")
            self.log.info("Twitch: UnMute")

    def playStream(self, playButton) -> None:
        """
        Clicks on the play button of a stream.

        Args:
            playButton: WebElement - The WebElement corresponding to the play button of the stream.

        Returns:
            None
        """
        try:
            playButton.click()
            self.log.info("Twitch: Play")
            print("Twitch: Play")
        except Exception:
            self.driver.execute_script("arguments[0].click();", playButton)
            print("Twitch: Play")
            self.log.info("Twitch: Play")
