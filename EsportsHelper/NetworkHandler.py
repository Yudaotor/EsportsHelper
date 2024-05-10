import json

from selenium.common import WebDriverException

from EsportsHelper.Config import config
from EsportsHelper.Logger import log
from EsportsHelper.I18n import i18n
from EsportsHelper.Stats import stats
_ = i18n.getText
_log = i18n.getLog


class NetworkHandler:
    def __init__(self, driver):
        self.driver = driver
        pass


def getRewardByLog(driver, isInit=False):
    """
    Extract reward and watch hour data from browser performance logs.

    This function retrieves reward and watch hour data from the browser's performance logs. It parses the logs and extracts
    the relevant information, updating the appropriate statistics variables accordingly.

    Parameters:
    driver: WebDriver instance representing the browser.
    isInit (bool): Flag indicating whether the data is for initialization or not. Defaults to False.

    """
    try:
        performanceLog = driver.get_log('performance')
        for packet in performanceLog:
            message = json.loads(packet.get('message')).get('message')
            if message.get('method') != 'Network.responseReceived':
                continue
            packetType = message.get('params').get('response').get('mimeType')
            if packetType != "application/json" and packetType != "text/plain":
                continue
            requestId = message.get('params').get('requestId')
            url = message.get('params').get('response').get('url')
            try:
                if "earnedDrops" in url:
                    resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})
                    dropList = json.loads(resp["body"])
                    if isInit:
                        stats.initDropsList = dropList
                    else:
                        stats.currentDropsList = dropList
                if "stats?sport=lol" in url:
                    resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})
                    watchHour = json.loads(resp["body"])[0]["statValue"]
                    if isInit:
                        stats.initWatchHour = watchHour
                    else:
                        stats.currentWatchHour = watchHour

            except WebDriverException:
                pass
        log.info(_log("获取日志数据"))
    except Exception:
        log.error(_log("获取日志数据失败"))


