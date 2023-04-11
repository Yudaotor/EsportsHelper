import undetected_chromedriver as uc
from rich import print
from webdriver_manager.chrome import ChromeDriverManager


class Webdriver:
    def __init__(self, config) -> None:
        self.config = config

    def createWebdriver(self):
        options = self.addWebdriverOptions(uc.ChromeOptions())
        print("[green]ㅍ_ㅍ 正在准备中...")
        if self.config.platForm == "linux":
            return uc.Chrome(options=options)
        elif self.config.platForm == "windows":
            chromeDriverManager = ChromeDriverManager(path=".\\driver")
            version = int(
                chromeDriverManager.driver.get_version().split(".")[0])
            driverPath = chromeDriverManager.install()
            if self.config.chromePath != "":
                return uc.Chrome(options=options, driver_executable_path=driverPath, version_main=version, browser_executable_path=self.config.chromePath)
            else:
                return uc.Chrome(options=options, driver_executable_path=driverPath, version_main=version)
        else:
            print("[red]不支持的操作系统")

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
        if self.config.proxy != "":
            options.add_argument(f"--proxy-server={self.config.proxy}")
        if self.config.headless:
            options.add_argument("--headless")
            windows_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44"
            mac_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            user_agent = windows_agent if self.config.platForm == "windows" else mac_agent
            options.add_argument(f'user-agent={user_agent}')
        return options
