import os
import time
from datetime import datetime, timedelta
from random import randint
from time import sleep
from traceback import format_exc
from EsportsHelper.Logger import log
from EsportsHelper.Config import config
from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.Utils import (Utils, OVERRIDES,
                                 getLolesportsWeb,
                                 getMatchName, sysQuit,
                                 getSleepPeriod, acceptCookies)
from EsportsHelper.Logger import delimiterLine
from EsportsHelper.YouTube import YouTube
from rich import print
from selenium.common import NoSuchElementException, NoSuchWindowException
from selenium.webdriver.common.by import By
from EsportsHelper.I18n import i18n
_ = i18n.getText
_log = i18n.getLog


class Match:
    def __init__(self, driver) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.utils = Utils()
        self.youtube = YouTube(driver=driver, utils=self.utils)
        self.twitch = Twitch(driver=driver, utils=self.utils)
        self.rewards = Rewards(
            driver=driver, youtube=self.youtube, utils=self.utils, twitch=self.twitch)
        self.currentWindows = {}
        self.rewardWindow = None
        self.mainWindow = self.driver.current_window_handle
        self.OVERRIDES = OVERRIDES
        self.sleepBeginList = []
        self.sleepEndList = []
        self.nextMatchHour = None
        self.nextMatchDay = None

    def watchMatches(self):
        """
           Watch live matches and earn rewards.
        """
        try:
            sleepFlag = False
            isSleep = False
            openDatetime = datetime.now()
            formattedOpenDatetime = openDatetime.strftime("%Y-%m-%d %H:%M:%S")
            self.currentWindows = {}
            self.mainWindow = self.driver.current_window_handle
            maxRunSecond = config.maxRunHours * 3600
            startTimePoint = time.time()
            endTimePoint = startTimePoint + maxRunSecond
            acceptCookies(driver=self.driver)
            if self.config.countDrops and sleepFlag is False:
                # Open the Rewards page
                self.rewardWindow = self.rewards.getRewardPage(newTab=True)
            # Gets the sleep period
            if self.config.sleepPeriod != [""]:
                self.sleepBeginList, self.sleepEndList = getSleepPeriod()
            delimiterLine()
            # 循环观赛
            while config.maxRunHours < 0 or time.time() < endTimePoint:
                sleep(1)
                self.log.info(_log("开始检查..."))
                print(_("开始检查...", color="green"))
                self.driver.switch_to.window(self.mainWindow)
                # Random numbers, used for random delay
                randomDelay = randint(int(config.delay * 0.08), int(config.delay * 0.15))
                newDelay = randomDelay * 10
                nowTimeHour = int(time.localtime().tm_hour)
                nowTimeDay = int(time.localtime().tm_mday)
                matches = []
                sleepEndTime = ""
                # If you are not currently sleeping,
                # get match information (including matches that are still counting down).
                if isSleep is False:
                    print(f'--{_("检查赛区直播状态...", color="green")}')
                    self.log.info(_log("检查赛区直播状态..."))
                    matches = self.getMatchInfo(ignoreBroadCast=False)
                if self.config.autoSleep:
                    # When the next game time is correct, go into sleep judgment.
                    if self.nextMatchHour is not None and self.nextMatchDay is not None:
                        # If the next match is on the same day as now, but the current time has exceeded the match time, sober up.
                        if nowTimeDay == self.nextMatchDay and \
                                nowTimeHour >= self.nextMatchHour:
                            isSleep = False
                        # If the next match is on the same day as the current day,
                        # and there is still over an hour before the match starts,
                        # and no regions are currently live-streaming, then enter a one-hour sleep mode.
                        elif nowTimeDay == self.nextMatchDay and \
                                nowTimeHour < self.nextMatchHour - 1 and \
                                self.currentWindows == {} and matches == []:
                            isSleep = True
                            newDelay = 3599
                            sleepEndTime = self.nextMatchHour
                        # If the next game is the same day as now, but the current time is already an hour before the game, sober up.
                        elif nowTimeDay == self.nextMatchDay and \
                                nowTimeHour == self.nextMatchHour - 1:
                            isSleep = False
                        # If the next game date is greater than the current date, and there is no live game now,
                        # and the current time hours are less than 23, sleep is entered with an interval of one hour.
                        elif nowTimeDay < self.nextMatchDay and self.currentWindows == {} \
                                and nowTimeHour < 23 and matches == []:
                            isSleep = True
                            sleepEndTime = _log("日期: ") + str(self.nextMatchDay) + " | " + str(self.nextMatchHour)
                            newDelay = 3599
                        elif nowTimeDay < self.nextMatchDay and nowTimeHour >= 23:
                            isSleep = False
                        else:
                            isSleep = False
                    # Stay awake when the next game time is wrong.
                    else:
                        isSleep = False
                else:
                    if self.nextMatchHour is not None and self.nextMatchDay is not None:
                        if nowTimeDay < self.nextMatchDay and self.currentWindows == {} and nowTimeHour < 23 and matches == []:
                            newDelay = 3599
                        # When the time of the next game is longer than 1 hour from the current time, the check interval is one hour
                        elif nowTimeHour < self.nextMatchHour - 1 and self.currentWindows == {} and matches == []:
                            newDelay = 3599
                # The sleep period set has a higher priority than the autoSleep function.
                if self.sleepBeginList == [] and self.sleepEndList == []:
                    pass
                else:
                    nowTimeHour = int(time.localtime().tm_hour)
                    for sleepBegin, sleepEnd in zip(self.sleepBeginList, self.sleepEndList):
                        if sleepBegin <= nowTimeHour < sleepEnd:
                            if nowTimeHour < sleepEnd - 1:
                                newDelay = 3599
                            else:
                                randomDelay = randint(
                                    int(config.delay * 0.08), int(config.delay * 0.15))
                                newDelay = randomDelay * 10
                            isSleep = True
                            sleepEndTime = sleepEnd
                            break
                        else:
                            isSleep = False

                if isSleep:
                    if sleepFlag is False:
                        print(_("进入休眠时间", color="green"))
                        self.log.info(_log("进入休眠时间"))
                        self.closeAllTabs()
                        sleepFlag = True
                    else:
                        print(_("处于休眠时间...", color="green"))
                        self.log.info(_log("处于休眠时间..."))
                    print(f'--{_("预计休眠状态将持续到", color="bold yellow")} '
                          f'[cyan]{sleepEndTime}[/cyan] '
                          f'{_("点", color="bold yellow")}')
                    self.log.info(f'{_log("预计休眠状态将持续到")} '
                                  f'{sleepEndTime} '
                                  f'{_log("点")}')
                    print(
                        f"{_('下次检查在:', color='bold yellow')} "
                        f"[cyan]{(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                    self.log.info(
                        f"{_log('下次检查在:')} "
                        f"{(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                    delimiterLine()
                    self.log.info(f"{'=' * 50}")
                    sleep(newDelay)
                    continue
                elif sleepFlag is True:
                    print(_("休眠时间结束", color="green"))
                    self.log.info(_log("休眠时间结束"))
                    sleepFlag = False
                    if self.config.countDrops:
                        self.driver.switch_to.window(self.rewardWindow)
                        self.rewardWindow = self.rewards.getRewardPage()

                # Get the number of drops and total hours watched
                if self.config.countDrops:
                    dropsNumber, dropsSessionInfo = self.rewards.countDrops(rewardWindow=self.rewardWindow)
                    self.driver.switch_to.window(self.mainWindow)
                    watchHours = self.rewards.totalWatchHours
                    sessionDrops = dropsNumber - self.rewards.historyDrops
                    if dropsNumber != -1 and sessionDrops >= 0:
                        print(
                            f"{_('生涯总掉落:', color='bold yellow')}{dropsNumber} | "
                            f"{_('总观看时长: ', color='bold yellow')}{watchHours}")
                        print(f"{_('程序启动时间: ', color='bold yellow')} "
                              f"[cyan]{formattedOpenDatetime}[/cyan] | "
                              f"{_('运行掉落总和:', color='bold yellow')}"
                              f"{sessionDrops}")
                        self.log.info(
                            f"{_log('程序启动时间: ')}"
                            f"{formattedOpenDatetime} | "
                            f"{_log('运行掉落总和:')}"
                            f"{sessionDrops} | "
                            f"{_log('生涯总掉落:')}"
                            f"{dropsNumber} | "
                            f"{_log('总观看时长: ')}"
                            f"{watchHours}")
                        if len(dropsSessionInfo) != 0:
                            print(
                                f"--{_('本次运行掉落详细:', color='bold yellow')} "
                                f"[bold cyan]{dropsSessionInfo}[/bold cyan]")
                            self.log.info(
                                f"{_log('本次运行掉落详细:')} "
                                f"{dropsSessionInfo}")
                    elif sessionDrops < 0:
                        self.log.error(_log("统计掉落数出错,掉落数小于0"))
                # Make sure to come to the lolesports schedule page
                try:
                    getLolesportsWeb(self.driver)
                except Exception:
                    self.log.error(format_exc())
                    self.log.error(_log("无法打开Lolesports网页，网络问题，将于3秒后退出..."))
                    self.utils.errorNotify(error=_log("无法打开Lolesports网页，网络问题"))
                    print(_("无法打开Lolesports网页，网络问题，将于3秒后退出...", color="red"))
                    sysQuit(self.driver, _log(
                        "无法打开Lolesports网页，网络问题，将于3秒后退出..."))

                matches = self.getMatchInfo()
                sleep(2)
                matchesLen = len(matches)
                if matchesLen == 0:
                    self.log.info(_log("没有赛区正在直播"))
                    print(_("没有赛区正在直播", color="green"))
                # 1 match
                elif matchesLen == 1:
                    self.log.info(
                        f"{matchesLen} {_log('个赛区正在直播中')}")
                    print(
                        f"{matchesLen} {_('个赛区正在直播中', color='green')}")
                # multiple matches
                else:
                    self.log.info(
                        f"{matchesLen} {_log('赛区正在直播中')}")
                    print(
                        f"{matchesLen} {_('赛区正在直播中', color='green')}")
                # Close the live streams of the regions that have already ended.
                self.closeFinishedTabs(liveMatches=matches)
                # Start watching the new live broadcast.
                self.startWatchNewMatches(
                    liveMatches=matches, disWatchMatches=self.config.disWatchMatches)
                sleep(3)
                # Switch back to main page.
                self.driver.switch_to.window(self.mainWindow)
                # Check information of the most recent match.
                self.checkNextMatch()
                if newDelay == 3599:
                    print(_("识别到距离比赛时间较长 检查间隔为1小时", color="green"))
                    self.log.info(_log("识别到距离比赛时间较长 检查间隔为1小时"))
                self.log.info(
                    f"{_log('下次检查在:')} "
                    f"{(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                self.log.info(f"{'=' * 50}")
                print(
                    f"{_('下次检查在:', color='bold yellow')} [cyan]"
                    f"{(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                if config.maxRunHours != -1:
                    print(
                        f"{_('预计结束程序时间:', color='green')} [cyan]"
                        f"{time.strftime('%H:%M', time.localtime(endTimePoint))}")
                delimiterLine()
                sleep(newDelay)
            if time.time() >= endTimePoint and config.maxRunHours != -1 and self.config.platForm == "windows":
                self.log.info(_log("程序设定运行时长已到，将于60秒后关机,请及时做好准备工作"))
                print(_("程序设定运行时长已到，将于60秒后关机,请及时做好准备工作", color="yellow"))
                os.system("shutdown -s -t 60")

        except NoSuchWindowException:
            self.log.error(_log("对应窗口找不到"))
            print(_("对应窗口找不到", color="red"))
            self.log.error(format_exc())
            self.utils.errorNotify(_log("对应窗口找不到"))
            sysQuit(self.driver, _log("对应窗口找不到"))
        except Exception:
            self.log.error(_log("发生错误"))
            print(_("发生错误", color="red"))
            self.log.error(format_exc())
            self.utils.errorNotify(_log("发生错误"))
            sysQuit(self.driver, _log("发生错误"))

    def getMatchInfo(self, ignoreBroadCast=True):
        """
        Function: getMatchInfo
        Description: Fetches the URLs of the live matches from the lolesports website.

        Input:
        - ignoreBroadCast: A boolean value indicating whether to ignore broadcast matches or not.

        Output:
        - matches: A list containing the URLs of the live matches.

        Exceptions:
        - If an exception occurs while fetching the URLs of the live matches, it logs the error message and returns an empty list.
        """
        try:
            matches = []
            # Make sure it is the latest page information.
            self.driver.refresh()
            sleep(2)
            trueMatchElements = self.driver.find_elements(
                by=By.CSS_SELECTOR, value=".EventMatch .event.live")
            matchElements = self.driver.find_elements(
                by=By.CSS_SELECTOR, value=".event.live")
            if self.config.ignoreBroadCast and ignoreBroadCast:
                for element in trueMatchElements:
                    matches.append(element.get_attribute("href"))
            else:
                for element in matchElements:
                    matches.append(element.get_attribute("href"))
            return matches
        except Exception:
            self.log.error(_log("获取比赛列表失败"))
            print(_("获取比赛列表失败", color="red"))
            self.log.error(format_exc())
            return []

    def closeAllTabs(self):
        """
        Closes all open tabs about lolesports.
        """
        try:
            removeList = []
            newTab1 = None
            if self.config.countDrops:
                self.driver.switch_to.new_window('tab')
                newTab1 = self.driver.current_window_handle
                sleep(1)
            self.driver.switch_to.new_window('tab')
            newTab2 = self.driver.current_window_handle
            sleep(1)
            for keys in self.currentWindows.keys():
                self.driver.switch_to.window(self.currentWindows[keys])
                sleep(1)
                self.driver.close()
                removeList.append(keys)
                sleep(1)
            self.driver.switch_to.window(self.mainWindow)
            sleep(1)
            self.driver.close()
            self.mainWindow = newTab2
            sleep(1)
            if self.config.countDrops:
                self.driver.switch_to.window(self.rewardWindow)
                sleep(1)
                self.driver.close()
                self.rewardWindow = newTab1
            for handle in removeList:
                self.currentWindows.pop(handle, None)
            print(f'--{_("所有窗口已关闭", color="green")}')
            self.log.info(_log("所有窗口已关闭"))
        except Exception:
            self.log.error(_log("关闭所有窗口时发生异常"))
            print(f'--{_("关闭所有窗口时发生异常", color="red")}')
            self.utils.errorNotify(error=_log("关闭所有窗口时发生异常"))
            self.log.error(format_exc())

    def closeFinishedTabs(self, liveMatches):
        """
        Close the Ended Contests tab and update the self.currentWindows dictionary.

        Args:
            liveMatches: A list of matches in the live stream with a link to the match.

        """
        try:
            removeList = []
            for keys in self.currentWindows.keys():
                self.driver.switch_to.window(self.currentWindows[keys])
                sleep(1)
                if keys not in liveMatches:
                    match = getMatchName(keys)
                    self.log.info(
                        f"{match} {_log('比赛结束')}")
                    print(
                        f"[bold magenta]{match}[/bold magenta] "
                        f"{_('比赛结束', color='green')}")
                    self.driver.close()
                    removeList.append(keys)
                    sleep(2)
                    self.driver.switch_to.window(self.mainWindow)
                    sleep(3)
                else:
                    if keys in self.OVERRIDES:
                        self.rewards.checkMatches("twitch", keys)
                    else:
                        self.rewards.checkMatches("youtube", keys)
            for keys in removeList:
                self.currentWindows.pop(keys, None)
            self.driver.switch_to.window(self.mainWindow)
        except Exception:
            print(_("关闭已结束的比赛时发生错误", color="red"))
            self.utils.errorNotify(error=_log("关闭已结束的比赛时发生错误"))
            self.log.error(format_exc())

    def startWatchNewMatches(self, liveMatches, disWatchMatches):
        """
        startWatchNewMatches method opens new browser tabs for each live match that is not already being watched,
        and skips matches that are in the disWatchMatches list.
        It then switches to the new tab and loads the stream URL, setting the quality to the desired level if possible.

        Args:
        - liveMatches (list): a list of strings representing the names or URLs of live matches.
        - disWatchMatches (list): a list of strings representing the names or keywords of matches to be skipped.

        """
        newLiveMatches = set(liveMatches) - set(self.currentWindows.keys())
        disWatchMatchesSet = set(disWatchMatches)
        for match in newLiveMatches:
            if any(disMatch in match for disMatch in disWatchMatchesSet):
                skipName = getMatchName(match)
                self.log.info(f"{skipName} {_log('比赛跳过')}")
                print(f"[bold magenta]{skipName}[/bold magenta] "
                      f"{_('比赛跳过', color='yellow')}")
                continue

            self.driver.switch_to.new_window('tab')
            sleep(1)
            self.currentWindows[match] = self.driver.current_window_handle
            # Identified as a Twitch stream.
            if match in self.OVERRIDES:
                url = self.OVERRIDES[match]
                self.driver.get(url)
                if not self.rewards.checkMatches("twitch", url):
                    return
                if self.config.closeStream:
                    self.closeStream()
                else:
                    try:
                        if self.twitch.setTwitchQuality():
                            self.log.info(_log("Twitch 160p清晰度设置成功"))
                            print(f'--{_("Twitch 160p清晰度设置成功", color="green")}')
                        else:
                            self.log.error(_log("Twitch 清晰度设置失败"))
                            print(f'--{_("Twitch 160p清晰度设置失败", color="red")}')
                    except Exception:
                        self.log.error(_log("无法设置 Twitch 清晰度."))
                        print(f'--{_("无法设置 Twitch 清晰度.", color="red")}')
                        self.log.error(format_exc())
            # Identified as a YouTube stream.
            else:
                url = match
                self.driver.get(url)
                # It is convenient to add to overrides next time
                self.log.info(self.driver.current_url)
                self.youtube.checkYoutubeStream()
                # When rewards are not currently available, no need to set the quality
                if not self.rewards.checkMatches("youtube", url):
                    return
                # remove the YouTube stream
                if self.config.closeStream:
                    self.closeStream()
                else:
                    try:
                        if self.youtube.setYoutubeQuality():
                            self.log.info(_log("Youtube 144p清晰度设置成功"))
                            print(f'--'
                                  f'{_("Youtube 144p清晰度设置成功", color="green")}')
                        else:
                            self.utils.debugScreen(self.driver, "youtube")
                            self.log.error(
                                _log("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者"))
                            print(f'--'
                                  f'{_("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者", color="red")}')
                    except Exception:
                        self.utils.debugScreen(self.driver, "youtube")
                        self.log.error(
                            _log("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者"))
                        print(f'--'
                              f'{_("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者", color="red")}')
                        self.log.error(format_exc())
            sleep(4)

    def closeStream(self):
        """
        Close the current video stream by removing the video player element from the DOM.
        """
        try:
            self.driver.execute_script("""var data=document.querySelector('#video-player').remove()""")
        except Exception:
            self.log.error(_log("关闭视频流失败."))
            print(f'--{_("关闭视频流失败.", color="red")}')
            self.log.error(format_exc())
        else:
            self.log.info(_log("视频流关闭成功."))
            print(f'--{_("视频流关闭成功.", color="green")}')

    def checkNextMatch(self):
        """
        Function: checkNextMatch
        Description: This function retrieves the details of the next upcoming match from the webpage and
                     compares it with the current date and time to determine if the match is still valid.
                     If the match is not valid, it will print a message indicating that the match has been filtered out.
                     If the match is valid, it will print the details of the next match.
        """
        try:
            nextMatchDayTime = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate > div.date > span.monthday").text
            timeList = nextMatchDayTime.split(" ")
            getNextMatchRetryTimes = 4
            while len(timeList) != 2 and getNextMatchRetryTimes > 0:
                getNextMatchRetryTimes -= 1
                self.utils.debugScreen(self.driver, "nextMatch")
                self.driver.refresh()
                sleep(5)
                nextMatchDayTime = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate > div.date > span.monthday").text
                timeList = nextMatchDayTime.split(" ")
            if len(timeList) != 2:
                self.log.error(_log("获取下一场比赛时间失败"))
                print(_("获取下一场比赛时间失败", color="red"))
                self.nextMatchDay = None
                return

            nextMatchMonth = timeList[0]
            nextMatchDay = int(timeList[1])
            nextMatchTime = self.driver.find_element(
                by=By.CSS_SELECTOR,
                value="div.divider.future + div.EventDate + div.EventMatch > div > div.EventTime > div > span.hour").text
            try:
                nextMatchAMOrPM = self.driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="div.divider.future + div.EventDate + div.EventMatch > div > div.EventTime > div > span.hour ~ span.ampm").text
            except NoSuchElementException:
                nextMatchAMOrPM = ""
            nextMatchLeague = self.driver.find_element(
                by=By.CSS_SELECTOR,
                value="div.divider.future + div.EventDate + div.EventMatch > div > div.league > div.name").text
            nextMatchBO = self.driver.find_element(
                by=By.CSS_SELECTOR,
                value="div.divider.future + div.EventDate + div.EventMatch > div > div.league > div.strategy").text
            if nextMatchAMOrPM == "PM" and nextMatchTime != "12":
                nextMatchStartHour = int(nextMatchTime) + 12
            elif nextMatchAMOrPM == "AM" and nextMatchTime == "12":
                nextMatchStartHour = 0
            else:
                nextMatchStartHour = int(nextMatchTime)
            self.nextMatchHour = nextMatchStartHour
            self.nextMatchDay = nextMatchDay
            invalidMatch = nextMatchLeague
            nowHour = int(time.localtime().tm_hour)
            nowMonth = time.strftime("%b", time.localtime())
            nowDay = int(time.strftime("%d", time.localtime()))
            if (nowMonth in nextMatchMonth and nowDay == nextMatchDay and nowHour > nextMatchStartHour) or \
                    (nowMonth not in nextMatchMonth and nowDay < nextMatchDay) or \
                    (nowMonth in nextMatchMonth and nowDay > nextMatchDay):
                nextMatchTime = self.driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.EventTime > div > span.hour").text
                nextMatchAMOrPM = self.driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.EventTime > div > span.hour ~ span.ampm").text
                nextMatchLeague = self.driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.league > div.name").text
                nextMatchBO = self.driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.league > div.strategy").text
                print(f'{_("(检查下一场比赛时 过滤失效的比赛 ->", color="yellow")} '
                      f'[yellow]{invalidMatch})')

                if nextMatchTime == "" or nextMatchLeague == "":
                    nextMatchTime = self.driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="div.single.future.event > div.EventTime > div > span.hour").text
                    nextMatchAMOrPM = self.driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="div.single.future.event > div.EventTime > div > span.hour ~ span.ampm").text
                    nextMatchLeague = self.driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="div.single.future.event > div.league > div.name").text
                    nextMatchBO = self.driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="div.single.future.event > div.league > div.strategy").text
                print(
                    f"{_('下一场比赛时间:', color='bold yellow')} "
                    f"[cyan]{nextMatchTime}{nextMatchAMOrPM}[/cyan] | "
                    f"[magenta]{nextMatchLeague}[/magenta] | "
                    f"[blue]{nextMatchBO}[/blue]")
                self.nextMatchDay = None
            else:
                print(
                    f"{_('下一场比赛时间:', color='bold yellow')} "
                    f"[cyan]{nextMatchDayTime}[/cyan] | "
                    f"[cyan]{nextMatchTime}{nextMatchAMOrPM}[/cyan] | "
                    f"[magenta]{nextMatchLeague}[/magenta] | "
                    f"[bold blue]{nextMatchBO}[/bold blue]")
        except Exception:
            self.log.error(_log("获取下一场比赛时间失败"))
            self.log.error(format_exc())
            print(_("获取下一场比赛时间失败", color="red"))
