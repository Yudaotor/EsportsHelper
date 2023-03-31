import subprocess
import sys
import time
from rich import print
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager


def info():
    print("[green]=========================================================")
    print(
        f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{VersionManager.getVersion()}!        [green]========[/green]")
    print("[green]============[/green] 本程序开源于github链接地址如下: [green]============[/green]")
    print("[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
    print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
    print("[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
    print("[green]====[/green] 如需关闭请勿直接右上角×关闭，请按Ctrl+C来关闭. [green]====[/green]")
    print("[green]=========================================================")
    print()
    VersionManager.checkVersion()


def Quit(driver=None, e=None):
    if driver:
        driver.quit()
    log.error(e)
    log.info("[red]------程序退出------")
    sys.exit()


def DebugScreen(driver, lint="", debug=True):
    if debug:
        driver.save_screenshot(f"./logs/pics/{time.strftime('%b-%d-%H-%M-%S')}-{lint}.png")
