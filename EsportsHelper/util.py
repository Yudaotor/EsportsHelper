import subprocess
import sys
import time

from EsportsHelper.Logger import log



def KnockNotify(msg):
     subprocess.run(f"source ~/.personalrc; knock {msg}", shell=True)


def Quit(driver=None, e=None):
     if e:
          KnockNotify(f"🥵停止挂机: '{e}'");

     if driver:
          driver.quit()
     log.error(e)
     log.info("[red]------程序退出------")
     sys.exit()


def DebugScreen(driver, lint="checkNewXDrogs", debug=True):
     if debug:
          driver.save_screenshot( f"./logs/pics/{time.strftime('%b-%d-%H-%M-%S')}-{lint}.png" )
