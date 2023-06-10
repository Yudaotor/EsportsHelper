from time import sleep
from traceback import format_exc
from rich import print
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from EsportsHelper.Logger import log
from EsportsHelper.Config import config
from EsportsHelper.I18n import i18n
_ = i18n.getText
_log = i18n.getLog


class YouTube:
    def __init__(self, driver, utils) -> None:
        self.driver = driver
        self.log = log
        self.config = config
        self.utils = utils
        self.wait = WebDriverWait(self.driver, 20)

    def checkYoutubeStream(self) -> bool:
        """
        This function checks if the YouTube livestream can be played, and resumes playing or unmute the video if it is paused or muted.

        Returns:
            bool: Returns True if the check is successful, otherwise returns False.
        """
        if self.config.closeStream:
            return True
        try:
            self.wait.until(ec.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[id=video-player-youtube]")))
            # If a video mute is detected, unmute it
            muteButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button.ytp-mute-button.ytp-button")))
            if muteButton.get_attribute("data-title-no-tooltip") == "Unmute":
                self.utils.debugScreen(self.driver, lint="Unmute")
                self.unmuteStream(muteButton)
            # Play if a video pause is detected
            playButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button.ytp-play-button.ytp-button")))
            if playButton.get_attribute("data-title-no-tooltip") == "Play":
                self.utils.debugScreen(self.driver, lint="Play")
                self.playStream(playButton)
            self.driver.switch_to.default_content()
            return True
        except Exception:
            self.log.error(_log("Youtube: 检查直播发生错误"))
            self.log.error(format_exc())
            self.driver.switch_to.default_content()
            return False

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
            print(_("Youtube: 解除暂停成功", color="green"))
            self.log.info(_log("Youtube: 解除暂停成功"))
        except Exception:
            print(_("Youtube: 解除暂停失败", color="red"))
            self.log.error(_log("Youtube: 解除暂停失败"))
            self.log.error(format_exc())

    def unmuteStream(self, muteButton) -> None:
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
            print(_("Youtube: 解除静音成功", color="green"))
            self.log.info(_log("Youtube: 解除静音成功"))
        except Exception:
            print(_("Youtube: 解除静音失败", color="red"))
            self.log.error(_log("Youtube: 解除静音失败"))
            self.log.error(format_exc())

    def setYoutubeQuality(self) -> bool:
        """
        Sets the video quality of a YouTube video being played.

        Returns:
        bool: True if the operation is successful, False otherwise.
        """
        try:
            self.wait.until(ec.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[id=video-player-youtube]")))
            settingsButton = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button.ytp-button.ytp-settings-button")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            sleep(1)
            try:
                qualityButton = self.wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.ytp-panel > div.ytp-panel-menu > div:nth-child(3)")))
            except Exception:
                qualityButton = self.wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.ytp-panel > div.ytp-panel-menu > div:nth-child(2)")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            sleep(1)
            option = self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.ytp-panel.ytp-quality-menu > div.ytp-panel-menu > div:nth-last-child(2)")))
            self.driver.execute_script("arguments[0].click();", option)
            self.driver.switch_to.default_content()
            return True
        except Exception:
            self.driver.switch_to.default_content()
            self.log.error(_log("Youtube: 设置清晰度时发生错误"))
            self.log.error(format_exc())
            self.utils.debugScreen(self.driver, lint="youtubeQuality")
            return False
