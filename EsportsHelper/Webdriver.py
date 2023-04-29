import undetected_chromedriver as uc
from EsportsHelper.Utils import _, _log
from rich import print
from webdriver_manager.chrome import ChromeDriverManager


class Webdriver:
    def __init__(self, config) -> None:
        self.config = config

    def createWebdriver(self):
        chromeDriverManager = ChromeDriverManager(path=".\\driver")
        options = self.addWebdriverOptions(uc.ChromeOptions())
        print(_("正在准备中...", color="yellow", lang=self.config.language))

        driverPath = chromeDriverManager.install()
        version = self.getDriverVersion(chromeDriverManager)

        kwargs = {
            "options": options,
            "driver_executable_path": driverPath,
            "version_main": version,
            "browser_executable_path": self.config.chromePath if self.config.chromePath else None,
            "user_data_dir": self.config.userDataDir if self.config.userDataDir else None,
        }
        return uc.Chrome(**{k: v for k, v in kwargs.items() if v})

    def getDriverVersion(self, chromeDriverManager):
        try:
            version = int(chromeDriverManager.driver.get_version().split(".")[0])
        except Exception:
            version = 108
        return version

    def addWebdriverOptions(self, options):
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
        if self.config.headless:
            options.add_argument("--headless=new")
            windows_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44"
            mac_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            user_agent = windows_agent if self.config.platForm == "windows" else mac_agent
            options.add_argument(f'user-agent={user_agent}')
        return options
