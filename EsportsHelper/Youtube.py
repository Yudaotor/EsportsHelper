from time import sleep
from traceback import format_exc, print_exc

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class Youtube:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log

    def playYoutubeStream(self):
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[id=video-player-youtube]")))
            playButton = wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div/div/div[27]/div[2]/div[1]/button")))
            # 当检测到视频暂停时，点击播放按钮
            streamStatus = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button.ytp-play-button.ytp-button > svg > use")))
            if streamStatus.get_attribute("href") == "#ytp-id-44":
                try:
                    playButton.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", playButton)
            # 离开播放器iframe
            self.driver.switch_to.default_content()
            return True
        except TimeoutException:
            self.log.error(format_exc())
            return False
        except Exception:
            self.log.error(format_exc())
            return False

    def setYoutubeQuality(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[id=video-player-youtube]")))
            settingsButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-tooltip-target-id=ytp-settings-button]")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            sleep(1)
            qualityButton = wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[25]/div/div/div[2]/div[3]")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            sleep(1)
            option = wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[25]/div/div[2]/div[6]/div")))
            self.driver.execute_script("arguments[0].click();", option)
            self.driver.switch_to.default_content()
            return True
        except TimeoutException:
            self.log.error(format_exc())
            return False
        except Exception:
            self.log.error(format_exc())
            return False
