import undetected_chromedriver as uc
from rich import print


class Webdriver:
    def __init__(self, headless) -> None:
        self.headless = headless

    def createWebdriver(self):
        options = self.addWebdriverOptions(uc.ChromeOptions())
        print("[green]正在准备中...")
        return uc.Chrome(options=options)

    def addWebdriverOptions(self, options):
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-audio-output')
        if self.headless:
            options.add_argument("--headless")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44"
            options.add_argument(f'user-agent={user_agent}')
        return options
