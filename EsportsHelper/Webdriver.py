import os
import undetected_chromedriver as uc
from rich import print
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from EsportsHelper.Config import config
from EsportsHelper.Logger import log
from EsportsHelper.I18n import i18n
_ = i18n.getText
_log = i18n.getLog


def getDriverVersion(chromeDriverManager):
    """
    Get the version number of the ChromeDriver being used by the driver instance.

    Args:
        chromeDriverManager (ChromeDriverManager): An instance of the ChromeDriverManager class.

    Returns:
        int: The version number of the ChromeDriver being used by the driver instance,
         or a default version of 108 if it is unable to retrieve the version number.
    """
    try:
        version = int(chromeDriverManager.driver.get_version().split(".")[0])
    except Exception:
        version = 108
    return version


class Webdriver:
    def __init__(self) -> None:
        self.config = config
        self.log = log

    def createWebdriver(self):
        """
        Creates a webdriver instance of uc.Chrome with specified options and configurations.

        Returns:
            A uc.Chrome instance.
        """
        customPath = ".\\driver"
        chromeDriverManager = ChromeDriverManager(cache_manager=DriverCacheManager(customPath))
        if self.config.isDockerized:
            driverPath = "/app/undetected_chromedriver/chromedriver"
        else:
            if self.config.platForm == "linux":
                if self.config.arm64:
                    username = os.getlogin()
                    driverPath = f"/home/{username}/.local/share/undetected_chromedriver/chromedriver"
                    if not os.path.exists(driverPath):
                        self.log.error(_log("找不到 chromedriver"))
                        return
                else:
                    customPath = "driver"
                    chromeDriverManager = ChromeDriverManager(cache_manager=DriverCacheManager(customPath))
                    driverPath = chromeDriverManager.install()
            elif self.config.platForm == "windows":
                customPath = ".\\driver"
                chromeDriverManager = ChromeDriverManager(cache_manager=DriverCacheManager(customPath))
                driverPath = chromeDriverManager.install()
            else:
                self.log.error(_("不支持的操作系统"))

        options = self.addWebdriverOptions(uc.ChromeOptions())
        print(_("正在准备中...", color="yellow"))
        self.log.info(_log("正在准备中..."))
        version = getDriverVersion(chromeDriverManager)

        kwargs = {
            "options": options,
            "driver_executable_path": driverPath,
            "version_main": version,
            "browser_executable_path": self.config.chromePath if self.config.chromePath else None,
            "user_data_dir": self.config.userDataDir if self.config.userDataDir else None,
        }
        return uc.Chrome(**{k: v for k, v in kwargs.items() if v})

    def addWebdriverOptions(self, options):
        """
        Adds options to a Chrome webdriver instance.

        Args:
        - options: An instance of ChromeOptions to which the options will be added.

        Returns:
        - An instance of ChromeOptions with the added options.

        Raises:
        - None
        """
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-audio-output')
        options.add_argument('--autoplay-policy=no-user-gesture-required')
        options.add_argument("--disable-gpu")
        prefs = {
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
        }
        options.add_experimental_option('prefs', prefs)
        if self.config.proxy:
            options.add_argument(f"--proxy-server={self.config.proxy}")
        if self.config.headless and not self.config.isDockerized:
            options.add_argument("--headless=new")
            
            windows_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
            mac_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            linux_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            
            if self.config.platForm == "windows":
                user_agent = windows_agent
            elif self.config.platForm == "mac":
                user_agent = mac_agent
            elif self.config.platForm == "linux":
                user_agent = linux_agent
            else:
                # Default to one agent, just in case
                user_agent = windows_agent
                
            options.add_argument(f'user-agent={user_agent}')
        return options
