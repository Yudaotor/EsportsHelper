from datetime import datetime
from time import sleep, strftime
from traceback import format_exc

from retrying import retry
from selenium import webdriver
import requests

from EsportsHelper.Drop import Drop
from EsportsHelper.NetworkHandler import NetworkHandler
from EsportsHelper.Utils import getMatchName, desktopNotify, checkRewardPage, \
    mouthTrans, formatExc, updateLiveInfo, updateLiveRegionsColor, \
    addRetrySuccessInfo, updateLiveDefinition, formatLeagueName, parseDropList, debugScreen, errorNotify
from rich import print
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from EsportsHelper.Config import config
from EsportsHelper.Logger import log
from EsportsHelper.I18n import i18n
from EsportsHelper.Stats import stats
#remove later
import json

_ = i18n.getText
_log = i18n.getLog
#self.latestProcessedDropTime = 1723204948000  # Force 8-aug date
class DropTracker:
    def __init__(self):
        self.latestProcessedDropTime = int(datetime.now().timestamp() * 1e3)

    def trackerCheckNewDrops(self, currentDropsList):
        # Sort drops by unlockedDateMillis in descending order
        sorted_drops = sorted(currentDropsList, key=lambda drop: drop.get("unlockedDateMillis", 0), reverse=True)

        newDropList = []
        
        for drop in sorted_drops:
            unlockedDateMillis = drop.get("unlockedDateMillis", -1)
            # Only add drops that are newer than the initial latestProcessedDropTime
            if unlockedDateMillis > self.latestProcessedDropTime:
                log.info(f" unlockedDateMillis: {unlockedDateMillis}")
                log.info(f" self.latestProcessedDropTime: {self.latestProcessedDropTime}")
                newDropList.append(drop)

        # Update latestProcessedDropTime if there are new drops
        if newDropList:
            self.latestProcessedDropTime = newDropList[0].get("unlockedDateMillis", self.latestProcessedDropTime)
        log.info(f" NEW self.latestProcessedDropTime: {self.latestProcessedDropTime}")
        return newDropList


class Rewards:
    def __init__(self, driver, youtube, twitch) -> None:
        self.driver = driver
        self.youtube = youtube
        self.twitch = twitch
        self.today = datetime.now().day
        self.networkHandler = NetworkHandler(driver=driver)
        self.wait = WebDriverWait(self.driver, 30)
        self.drop_tracker = DropTracker()


    def checkRewardsFlag(self, stream: str):
        """
        Checks if the reward mark exists on the current page.
        """
        try:
            # Check if the reward mark exists
            try:
                self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div[class=status-summary] g")))
            except Exception:
                log.error(_log("未找到奖励标识"))
            rewardImg = self.driver.find_elements(By.CSS_SELECTOR, "div[class=status-summary] g")
            if len(rewardImg) > 0:
                # Check stream
                if stream == "youtube":
                    if self.youtube.checkYoutubeStream():
                        return 1
                elif stream == "twitch":
                    if self.twitch.checkTwitchStream():
                        return 1

            # Check for VODs
            if len(self.driver.find_elements(By.CSS_SELECTOR, "main.Vods")) > 0:
                debugScreen(self.driver, "vods")
                return 0

            if stream == "twitch":
                result = self.twitch.checkTwitchIsOnline()
                if result == -1:
                    return 0
                elif result == 0:
                    pass
        except Exception:
            log.error(_log("检测奖励标识失败"))
            log.error(formatExc(format_exc()))
            debugScreen(self.driver, "reward")

        return -1

    def checkMatches(self, stream, url, retryTimes=6) -> bool:
        """
        Checks if rewards are available to be obtained from the given stream and URL.

        Args:
            stream (str): The name of the stream platform ("twitch" or "youtube").
            url (str): The URL of the stream.
            retryTimes (int, optional): The number of times to retry checking for rewards if the initial attempt fails. Default is 6.

        Returns:
            bool: True if rewards are available, False otherwise.
        """
        match = getMatchName(url)
        name = formatLeagueName(match)
        # Check if the match stream is correct
        if self.checkRewardsFlag(stream) == 1 and url not in self.driver.current_url and "emea" not in self.driver.current_url:
            log.info(self.driver.current_url + " " + url)
            log.warning(name + " " + _log("进错直播间,正在重新进入"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                              f"[bold magenta]{name}[/bold magenta] {_('进错直播间,正在重新进入', color='yellow')}")
            self.driver.get(url)
            sleep(3)
            if stream == "twitch":
                if config.closeStream:
                    try:
                        self.driver.execute_script("""var data=document.querySelector('#video-player').remove()""")
                    except Exception:
                        debugScreen(self.driver, "closeStreamElement")
                        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                          f"[bold magenta]{name}[/bold magenta] {_('关闭视频流失败', color='yellow')}")
                        log.error(name + " " + _log("关闭视频流失败."))
                        log.error(formatExc(format_exc()))
                    else:
                        updateLiveDefinition(match, "None")
                        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                          f"[bold magenta]{name}[/bold magenta] {_('视频流关闭成功', color='yellow')}")
                        log.info(name + " " + _log("视频流关闭成功."))
                else:
                    try:
                        if self.twitch.setTwitchQuality():
                            log.info(name + " " + _log("Twitch 160p清晰度设置成功"))
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]{name}[/bold magenta] {_('Twitch 160p清晰度设置成功', color='yellow')}")
                            updateLiveDefinition(match, "160p")
                        else:
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]{name}[/bold magenta] {_('Twitch 160p清晰度设置失败', color='yellow')}")
                            log.error(name + " " + _log("Twitch 清晰度设置失败"))
                    except Exception:
                        log.error(name + " " + _log("无法设置 Twitch 清晰度."))
                        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                          f"[bold magenta]{name}[/bold magenta] {_('无法设置 Twitch 清晰度', color='yellow')}")
                        log.error(formatExc(format_exc()))
            else:
                self.youtube.checkYoutubeStream()
                # remove the YouTube stream
                if config.closeStream:
                    try:
                        self.driver.execute_script("""var data=document.querySelector('#video-player').remove()""")
                    except Exception:
                        debugScreen(self.driver, "closeStreamElement")
                        log.error(name + " " + _log("关闭视频流失败."))
                        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                          f"[bold magenta]{name}[/bold magenta] {_('关闭视频流失败', color='yellow')}")
                        log.error(formatExc(format_exc()))
                    else:
                        updateLiveDefinition(match, "None")
                        log.info(name + " " + _log("视频流关闭成功."))
                        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                          f"[bold magenta]{name}[/bold magenta] {_('视频流关闭成功', color='yellow')}")
                else:
                    try:
                        if self.youtube.setYoutubeQuality():
                            log.info(name + " " + _log("Youtube 144p清晰度设置成功"))
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]{name}[/bold magenta] {_('Youtube 144p清晰度设置成功', color='yellow')}")
                            updateLiveDefinition(match, "144p")
                        else:
                            debugScreen(self.driver, "youtube")
                            log.error(name + " " + _log("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者"))
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]{name}[/bold magenta] {_('无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者', color='yellow')}")
                    except Exception:
                        debugScreen(self.driver, "youtube")
                        log.error(name + " " + _log("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者"))
                        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                          f"[bold magenta]{name}[/bold magenta] {_('无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者', color='yellow')}")
                        log.error(formatExc(format_exc()))

        viewerNumber = _log("出错, 未知")
        for i in range(retryTimes):
            flag = self.checkRewardsFlag(stream=stream)
            if flag == 1 and config.closeStream is False:
                try:
                    if stream == "twitch":
                        frameLocator = (By.CSS_SELECTOR, "iframe[title=Twitch]")
                        self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))

                        peopleLocator = (By.CSS_SELECTOR, "p[data-test-selector=stream-info-card-component__description]")
                        viewerInfoElement = self.wait.until(ec.presence_of_element_located(peopleLocator))
                        viewerInfo = viewerInfoElement.text
                        retryViewerTimes = 6
                        while not viewerInfo and retryViewerTimes > 0:
                            retryViewerTimes -= 1
                            if retryViewerTimes != 5:
                                debugScreen(self.driver, name + "viewerNumber")
                                log.warning(name + _log("获取观看人数信息重试中..."))
                            self.driver.switch_to.default_content()
                            self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))
                            webdriver.ActionChains(self.driver).move_to_element(viewerInfoElement).perform()
                            viewerInfo = self.wait.until(ec.presence_of_element_located(peopleLocator)).text
                            sleep(1)

                        viewerNumberFlag = True
                        for num in viewerInfo:
                            if num.isdigit() and viewerNumberFlag:
                                viewerNumber = "" + num
                                viewerNumberFlag = False
                                continue
                            if num.isdigit():
                                viewerNumber += num
                        self.driver.switch_to.default_content()

                except Exception:
                    self.driver.switch_to.default_content()
                    log.error(formatExc(format_exc()))
                if stream == "twitch":
                    if self.twitch.checkTwitchStream() is False:
                        self.driver.refresh()
                        updateLiveDefinition(match, "Auto")
                        sleep(8)
                        if self.twitch.setTwitchQuality():
                            updateLiveDefinition(match, "160p")
                        self.twitch.checkTwitchStream()
                    addRetrySuccessInfo(i, name)
                    updateLiveRegionsColor(match, "bold yellow")
                    updateLiveInfo(match, viewerNumber, "online", stream, url)
                    return True

                elif stream == "youtube":
                    if self.youtube.checkYoutubeStream() is False:
                        self.driver.refresh()
                        updateLiveDefinition(match, "Auto")
                        sleep(8)
                        if self.youtube.setYoutubeQuality():
                            updateLiveDefinition(match, "144p")
                        self.youtube.checkYoutubeStream()
                    addRetrySuccessInfo(i, name)
                    updateLiveRegionsColor(match, "bold yellow")
                    updateLiveInfo(match, viewerNumber, "online", stream, url)
                    return True
            # reward flag is ok, but closeStream is True
            elif flag == 1 and config.closeStream is True:
                updateLiveRegionsColor(match, "bold yellow")
                addRetrySuccessInfo(i, name)
                updateLiveInfo(match, viewerNumber, "online", stream, url)
                return True
            elif flag == 0:
                times = 1
                while times > 0:
                    self.driver.get(url)
                    updateLiveDefinition(match, "Auto")
                    nameUrl = getMatchName(url).lower()
                    times -= 1
                    sleep(3)
                    debugScreen(self.driver, name + " afterRefresh")
                    if self.checkRewardsFlag(stream=stream) == 1 and config.closeStream is False:
                        if stream == "twitch":
                            if self.twitch.setTwitchQuality():
                                updateLiveDefinition(match, "160p")
                            else:
                                updateLiveDefinition(match, "Auto")
                        elif stream == "youtube":
                            if self.youtube.setYoutubeQuality():
                                updateLiveDefinition(match, "144p")
                            else:
                                updateLiveDefinition(match, "Auto")
                        if nameUrl not in self.driver.current_url:
                            updateLiveRegionsColor(match, "dim yellow")
                            updateLiveInfo(match, viewerNumber, "offline", stream, url)
                        else:
                            updateLiveRegionsColor(match, "bold yellow")
                            addRetrySuccessInfo(i, name)
                            updateLiveInfo(match, viewerNumber, "online", stream, url)
                        debugScreen(self.driver, name + " afterRetry")
                        return True
                    elif self.checkRewardsFlag(stream=stream) == 1 and config.closeStream is True:
                        updateLiveRegionsColor(match, "bold yellow")
                        updateLiveInfo(match, viewerNumber, "online", stream, url)
                        return True
                    elif self.checkRewardsFlag(stream=stream) == 0:
                        debugScreen(self.driver, name + " afterVods")
                        continue
                updateLiveRegionsColor(match, "dim yellow")
                updateLiveInfo(match, viewerNumber, "offline", stream, url)

                return True
            elif flag == -1:
                if i != retryTimes - 1:
                    stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                      f"[bold magenta]{name}[/bold magenta] "
                                      f"{_('观看异常', color='red')}{(i + 1) * 15}{_('秒后重试', color='red')}")
                    updateLiveRegionsColor(match, "bold red")
                    updateLiveInfo(match, viewerNumber, "retry", stream, url)
                    waitTime = (i + 1) * 15
                    sleep(waitTime // 2)
                    self.driver.refresh()
                    sleep(waitTime // 2)
                    updateLiveDefinition(match, "Auto")
                    sleep(7)
                    if stream == "youtube":
                        if self.youtube.setYoutubeQuality():
                            updateLiveDefinition(match, "144p")
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]{name}[/bold magenta] "
                                              f"{_('Youtube 144p清晰度设置成功', color='green')}")
                        else:
                            updateLiveDefinition(match, "Auto")
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]{name}[/bold magenta] "
                                              f"{_('Youtube 144p清晰度设置失败', color='yellow')}")
                            sleep(5)
                            self.youtube.setYoutubeQuality()
                        if self.youtube.checkYoutubeStream() is False:
                            self.driver.refresh()
                            sleep(8)
                            if self.youtube.setYoutubeQuality():
                                updateLiveDefinition(match, "144p")
                                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                                  f"[bold magenta]{name}[/bold magenta] "
                                                  f"{_('Youtube 144p清晰度设置成功', color='green')}")
                            else:
                                updateLiveDefinition(match, "Auto")
                                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                                  f"[bold magenta]{name}[/bold magenta] "
                                                  f"{_('Youtube 144p清晰度设置失败', color='yellow')}")
                                sleep(5)
                                self.twitch.setTwitchQuality()
                            self.youtube.checkYoutubeStream()
                    if stream == "twitch":
                        if self.twitch.setTwitchQuality():
                            updateLiveDefinition(match, "160p")
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]" + name + "[/bold magenta] " +
                                              _("Twitch 160p清晰度设置成功", color="green"))
                        else:
                            updateLiveDefinition(match, "Auto")
                            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                              f"[bold magenta]{name}[/bold magenta] "
                                              f"{_('Twitch 160p清晰度设置失败', color='yellow')}")
                            sleep(5)
                            self.twitch.setTwitchQuality()
                        if self.twitch.checkTwitchStream() is False:
                            self.driver.refresh()
                            updateLiveDefinition(match, "160p")
                            sleep(8)
                            if self.twitch.setTwitchQuality():
                                updateLiveDefinition(match, "160p")
                            else:
                                updateLiveDefinition(match, "Auto")
                            self.twitch.checkTwitchStream()
                else:
                    stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                      f"[bold magenta]{name}[/bold magenta] "
                                      f"{_('观看异常', color='red')}")
                    updateLiveRegionsColor(match, "bold red")
                    updateLiveInfo(match, viewerNumber, "error", stream, url)
                    errorNotify(f"{name} {_log('观看异常')}")
                    return False

    @retry(stop_max_attempt_number=3, wait_incrementing_increment=10000, wait_incrementing_start=10000)
    def notifyDrops(self, drop: Drop):
        """
        Notifies about drops.

        Args:
        - drop: Drop object containing drop information.

        Returns:
        - bool: True if the notification was successful, False otherwise.
        """
        if config.notifyType in ["all", "drops"]:
            try:
                s = requests.session()
                s.keep_alive = False  # close connection after each request
                if "https://oapi.dingtalk.com" in config.connectorDropsUrl:
                    cappedInfo = " "
                    if str(drop.numberOfFansUnlocked) != "0" and drop.capped:
                        cappedInfo = f"**[{_log('稀有掉宝-概率')}]** {drop.numberOfFansUnlocked}/{drop.eligibleRecipients}"
                    btns = []
                    for reward in drop.rewardList:
                        btns.append({
                            "title": f"{reward}",
                            "actionURL": ""
                        })
                    data = {
                        "actionCard": {
                            "title": f"Drop:今:{stats.todayDrops} 总:{len(stats.currentDropsList)}",
                            "text": f"**Drop:今:{stats.todayDrops} 总:{len(stats.currentDropsList)}**  "
                                    f'![事件图]({drop.cardUrl})'
                                    f"**[{_log('昵称')}]** {config.nickName}\n\n"
                                    f"**[{_log('事件')}]** {drop.eventTitle}\n\n"
                                    f"**[{_log('赛区')}]** {drop.leagueName}\n\n"
                                    f"**[{_log('时间')}]** {drop.dropTime}\n\n"
                                    f"{cappedInfo}",
                            "btnOrientation": "1",
                            "btns": btns
                        },
                        "msgtype": "actionCard",
                    }
                    s.post(config.connectorDropsUrl, json=data)
                    s.close()
                    sleep(10)
                elif "https://discord" in config.connectorDropsUrl:
                    field0 = {
                        "name": f"{_log('昵称')}",
                        "value": f"{config.nickName}",
                        "inline": True
                    }
                    field1 = {
                        "name": f"{_log('事件')}",
                        "value": f"{drop.eventTitle}",
                        "inline": True
                    }
                    field2 = {
                        "name": f"{_log('掉落')}",
                        "value": f"{drop.rewardList}",
                        "inline": True
                    }
                    field4 = {
                        "name": f"{_log('时间')}",
                        "value": f"{drop.dropTime}",
                        "inline": True
                    }
                    field5 = {
                        "name": f"{_log('赛区')}",
                        "value": f"{drop.leagueName}",
                        "inline": True
                    }
                    fieldNone = {
                        "name": "",
                        "value": "",
                        "inline": True
                    }
                    field6 = {
                        "name": f"{_log('今日')}({_log('总')})",
                        "value": f"{stats.todayDrops}({len(stats.currentDropsList)})",
                        "inline": True
                    }
                    field7 = {
                        "name": f"{_log('稀有掉宝-概率')}",
                        "value": f"{drop.numberOfFansUnlocked}/{drop.eligibleRecipients}",
                        "inline": True
                    }
                    if str(drop.numberOfFansUnlocked) == "0" or drop.capped is False:
                        field7 = fieldNone
                    embed = {
                        "title": "Drop!",
                        "image": {"url": f"{drop.cardUrl}"},
                        "thumbnail": {"url": f"{drop.rewardImage}"},
                        "fields": [field0, field1, field7, field2, field4, field5, field6],
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    s.post(config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    s.close()
                    sleep(5)
                elif "https://fwalert.com" in config.connectorDropsUrl:
                    cappedInfo = " "
                    if str(drop.numberOfFansUnlocked) != "0" and drop.capped:
                        cappedInfo = f"[{_log('稀有掉宝-概率')}]{drop.numberOfFansUnlocked}/{drop.eligibleRecipients}"
                    params = {
                        "text": f"{_log('今天')} {stats.todayDrops} {_log('掉宝')} {_log('总')}:{len(stats.currentDropsList)}\n[{_log('昵称')}]{config.nickName}\n[{_log('事件')}]{drop.eventTitle}\n[{_log('掉落')}]{drop.rewardList}\n[{_log('赛区')}]{drop.leagueName} [{_log('时间')}]{drop.dropTime} {cappedInfo}",
                    }
                    s.post(config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    s.close()
                    sleep(10)
                elif "https://qyapi.weixin.qq.com" in config.connectorDropsUrl:
                    cappedInfo = " "
                    if str(drop.numberOfFansUnlocked) != "0" and drop.capped:
                        cappedInfo = f"[{_log('稀有掉宝-概率')}]{drop.numberOfFansUnlocked}/{drop.eligibleRecipients}"
                    params = {
                        "msgtype": "news",
                        "news": {
                            "articles": [
                                {
                                    "title": f"{_log('今天')} {stats.todayDrops} {_log('掉宝')} {_log('总')}:{len(stats.currentDropsList)}",
                                    "description": f"[{_log('昵称')}]{config.nickName}\n[{_log('事件')}]{drop.eventTitle}\n[{_log('掉落')}]{drop.rewardList}\n[{_log('赛区')}]{drop.leagueName}\n[{_log('时间')}]{drop.dropTime} {cappedInfo}",
                                    "url": "https://lolesports.com/rewards",
                                    "picurl": f"{drop.rewardImage}"
                                }
                            ]
                        }
                    }
                    s.post(config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    s.close()
                    sleep(10)
                elif "https://open.feishu.cn" in config.connectorDropsUrl:
                    cappedInfo = " "
                    if str(drop.numberOfFansUnlocked) != "0" and drop.capped:
                        cappedInfo = f"[{_log('稀有掉宝-概率')}]{drop.numberOfFansUnlocked}/{drop.eligibleRecipients}"
                    params = {
                        "msg_type": "text",
                        "content": {
                            "text": f"Drop:{_log('今天')} {stats.todayDrops} {_log('掉宝')} {_log('总')}:{len(stats.currentDropsList)}\n[{_log('昵称')}]{config.nickName}\n[{_log('事件')}]{drop.eventTitle}\n[{_log('掉落')}]{drop.rewardList}\n[{_log('赛区')}]{drop.leagueName} [{_log('时间')}]{drop.dropTime} {cappedInfo}",
                        }
                    }
                    s.post(config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    s.close()
                    sleep(10)
                else:
                    cappedInfo = " "
                    if str(drop.numberOfFansUnlocked) != "0" and drop.capped:
                        cappedInfo = f"[{_log('稀有掉宝-概率')}]{drop.numberOfFansUnlocked}/{drop.eligibleRecipients}"
                    params = {
                        "text": f"Drop:{_log('今天')} {stats.todayDrops} {_log('掉宝')} {_log('总')}:{len(stats.currentDropsList)}\n[{_log('昵称')}]{config.nickName}\n[{_log('事件')}]{drop.eventTitle}\n[{_log('掉落')}]{drop.rewardList}\n[{_log('赛区')}]{drop.leagueName} [{_log('时间')}]{drop.dropTime} {cappedInfo}",
                    }
                    s.post(config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    s.close()
                    sleep(10)
                log.info(_log("掉落提醒成功"))
                return True
            except Exception:
                log.error(_log("掉落提醒失败 重试中..."))
                log.error(formatExc(format_exc()))
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('掉落提醒失败 重试中...', color='red')}")
                return False

    def getRewardPage(self, newTab=False):
        """
        Open the rewards page in a new tab or the current tab and initialize drop count.

        :param newTab: Boolean indicating whether to open the rewards page in a new tab.
        :return: The window handle of the rewards page.
        """
        try:
            if newTab:
                self.driver.switch_to.new_window("tab")
            self.driver.get("https://lolesports.com/rewards")
            rewardWindow = self.driver.current_window_handle
            # Initialize drop count
            if newTab:
                checkRewardPage(self.driver, isInit=True)
            else:
                checkRewardPage(self.driver, isInit=False)
            return rewardWindow
        except Exception:
            debugScreen(self.driver, "getRewardPage")
            log.error(_log("检查掉落数失败"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('检查掉落数失败', color='red')}")
            log.error(formatExc(format_exc()))

    def checkNewDrops(self):
        #log.info("checkNewDrops called")
        """
        Check for new drops since the last check. If new drops are found, update relevant information and perform actions.

        """
        if self.today != datetime.now().day:
            self.today = datetime.now().day
            with open(f'./dropsHistory/{strftime("%Y%m%d-")}drops.txt', "a+"):
                pass
            stats.todayDrops = 0
        newDropList = self.drop_tracker.trackerCheckNewDrops(stats.currentDropsList)
        # newDropList = [drop for drop in stats.currentDropsList if drop.get("cappedDrop", False)]
        if newDropList:
            newDrops = parseDropList(newDropList)
            #log.info(f"Logging newDropList array: {json.dumps(newDropList, indent=2)}")
            for drop in newDrops:
                cappedInfo = " "
                if str(drop.numberOfFansUnlocked) != "0" and drop.capped:
                    cappedInfo = f"[{_log('稀有掉宝-概率')}]{drop.numberOfFansUnlocked}/{drop.eligibleRecipients}"
                stats.sessionDropsDict[drop.leagueName] = stats.sessionDropsDict.get(drop.leagueName, 0) + 1
                try:
                    with open('./dropsHistory/' + strftime("%Y%m%d-") + 'drops.txt', 'a+', encoding="utf-8") as f:
                        f.write(f"{drop.dropTime}--{config.nickName}--{drop.leagueName}--{drop.eventTitle}--{drop.rewardList}--{cappedInfo}\n")
                except Exception:
                    log.error(_log("写入掉落历史文件失败"))
                    stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('写入掉落历史文件失败', 'red')}")
                    log.error(formatExc(format_exc()))
                log.info(
                    f"<{config.nickName}>|{_log('今日')}| "
                    f"{stats.todayDrops} |{_log('通过')}| "
                    f"{drop.eventTitle} |{_log('获得')}| {drop.rewardList} "
                    f"|{_log('于')}| {drop.leagueName} | {drop.dropTime} {cappedInfo}")
                stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} "
                                  f"{_('今日', 'bold blue')}|{stats.todayDrops}|{_('于', 'bold blue')}|{drop.leagueName}"
                                  f"|{_('获得', 'bold blue')}|{drop.rewardList} {cappedInfo}")
                if config.desktopNotify:
                    desktopNotify(drop)
                if config.connectorDropsUrl != "":
                    try:
                        self.notifyDrops(drop)
                    except Exception:
                        log.error(_log("推送掉落失败"))
                        stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('推送掉落失败', 'red')}")
                        log.error(formatExc(format_exc()))
        else:
            pass
