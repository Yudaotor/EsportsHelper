import os
import time
from datetime import datetime, timedelta
from random import randint
from time import sleep
from traceback import format_exc

from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.Utils import (Utils, _, _log, desktopNotify,
                                 getLolesportsWeb,
                                 getMatchName, sysQuit)
from EsportsHelper.YouTube import YouTube
from rich import print
from selenium.common import NoSuchElementException, NoSuchWindowException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class Match:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.utils = Utils(config=config)
        self.youtube = YouTube(driver=driver, log=log)
        self.rewards = Rewards(
            log=log, driver=driver, config=config, youtube=self.youtube, utils=self.utils)
        self.twitch = Twitch(driver=driver, log=log)
        self.currentWindows = {}
        self.rewardWindow = None
        self.mainWindow = self.driver.current_window_handle
        self.OVERRIDES = self.utils.getOverrideFile()
        self.historyDrops = 0
        self.dropsDict = {}
        self.sleepBeginList = []
        self.sleepEndList = []
        self.nextMatchHour = None
        self.nextMatchDay = None
        self.isNotified = {}

    def watchMatches(self, delay, maxRunHours):
        """
           Watch live matches and earn rewards.

           Args:
               delay (int): Delay time between each check (in seconds).
               maxRunHours (int): The maximum number of hours to run the script. If set to -1, the script will run indefinitely.

        """
        try:
            sleepFlag = False
            isSleep = False
            self.currentWindows = {}
            self.mainWindow = self.driver.current_window_handle
            maxRunSecond = maxRunHours * 3600
            startTimePoint = time.time()
            endTimePoint = startTimePoint + maxRunSecond
            if self.config.countDrops and sleepFlag is False:
                # Open the Rewards page
                self.getRewardPage(newTab=True)
            # Gets the sleep period
            if self.config.sleepPeriod != [""]:
                self.getSleepPeriod()
            print(
                f"[bold yellow]>_<"
                f"{'=' * 27}"
                f">_<"
                f"{'=' * 27}"
                f">_<[/bold yellow]"
            )
            # 循环观赛
            while maxRunHours < 0 or time.time() < endTimePoint:
                sleep(1)
                self.log.info(_log("开始检查...", lang=self.config.language))
                print(_("开始检查...", color="green", lang=self.config.language))
                self.driver.switch_to.window(self.mainWindow)
                # Random numbers, used for random delay
                randomDelay = randint(int(delay * 0.08), int(delay * 0.15))
                newDelay = randomDelay * 10
                nowTimeHour = int(time.localtime().tm_hour)
                nowTimeDay = int(time.localtime().tm_mday)
                nowTimeMin = int(time.localtime().tm_min)
                matches = []
                # If you are not currently sleeping,
                # get match information (including races that are still counting down).
                if isSleep is False:
                    print(_("检查赛区直播状态...", color="green", lang=self.config.language))
                    self.log.info(_log("检查赛区直播状态...", lang=self.config.language))
                    matches = self.getMatchInfo(ignoreBroadCast=False)
                if self.config.autoSleep:
                    # When the next game time is correct, go into sleep judgment.
                    if self.nextMatchHour is not None and self.nextMatchDay is not None:
                        # If the next match is on the same day as now, but the current time has exceeded the match time, sober up.
                        if nowTimeDay == self.nextMatchDay and nowTimeHour >= self.nextMatchHour:
                            isSleep = False
                        # If the next match is on the same day as the current day,
                        # and there is still over an hour before the match starts,
                        # and no regions are currently live-streaming, then enter a one-hour sleep mode.
                        elif nowTimeDay == self.nextMatchDay and nowTimeHour < self.nextMatchHour - 1 and self.currentWindows == {} and matches == []:
                            isSleep = True
                            newDelay = 3599
                            sleepEndTime = self.nextMatchHour
                        # 如果下场比赛和现在是同一天,但是当前时间已经是比赛前的一个小时,就清醒.
                        elif nowTimeDay == self.nextMatchDay and nowTimeHour == self.nextMatchHour - 1:
                            isSleep = False
                        # 如果下场比赛日期大于现在日期,并且现在没有比赛直播,并且现在时间小时数小于23,就进入休眠,间隔为一小时
                        elif nowTimeDay < self.nextMatchDay and self.currentWindows == {} and nowTimeHour < 23 and matches == []:
                            isSleep = True
                            sleepEndTime = _("日期: ", color="cyan", lang=self.config.language) + str(self.nextMatchDay) + " | " + str(self.nextMatchHour)
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
                                    int(delay * 0.08), int(delay * 0.15))
                                newDelay = randomDelay * 10
                            isSleep = True
                            sleepEndTime = sleepEnd
                            break
                        else:
                            isSleep = False

                if isSleep:
                    if sleepFlag is False:
                        print(_("进入休眠时间", color="green", lang=self.config.language))
                        self.log.info(_log("进入休眠时间", lang=self.config.language))
                        self.closeAllTabs()
                        sleepFlag = True
                    else:
                        print(_("处于休眠时间...", color="green", lang=self.config.language))
                        self.log.info(_log("处于休眠时间...", lang=self.config.language))
                    print(f'{_("预计休眠状态将持续到", color="green", lang=self.config.language)} {sleepEndTime} {_("点", color="green", lang=self.config.language)}')
                    self.log.info(f'{_log("预计休眠状态将持续到", lang=self.config.language)} {sleepEndTime} {_log("点", lang=self.config.language)}')
                    print(
                        f"{_('下次检查在:', color='green', lang=self.config.language)} [cyan]{(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                    self.log.info(
                        f"{_log('下次检查在:', lang=self.config.language)} {(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                    print(
                        f"[bold yellow]>_<"
                        f"{'=' * 27}"
                        f">_<"
                        f"{'=' * 27}"
                        f">_<[/bold yellow]"
                    )
                    self.log.info(f"{'=' * 50}")
                    sleep(newDelay)
                    continue
                elif sleepFlag is True:
                    print(_("休眠时间结束", color="green", lang=self.config.language))
                    self.log.info(_log("休眠时间结束", lang=self.config.language))
                    sleepFlag = False
                    self.driver.switch_to.window(self.rewardWindow)
                    if self.config.countDrops:
                        self.getRewardPage()
                # Get the number of drops and total hours watched
                dropsNumber, watchHours = self.countDrops()
                self.driver.switch_to.window(self.mainWindow)
                if dropsNumber != -1:
                    print(
                        f"{_('本次运行掉落总和:', color='green', lang=self.config.language)}{dropsNumber - self.historyDrops} | "
                        f"{_('生涯总掉落:', color='green', lang=self.config.language)}{dropsNumber} | "
                        f"{_('总观看时长: ', color='green', lang=self.config.language)}{watchHours}")
                    self.log.info(
                        f"{_log('本次运行掉落总和:', lang=self.config.language)}{dropsNumber - self.historyDrops} | "
                        f"{_log('生涯总掉落:', lang=self.config.language)}{dropsNumber} | "
                        f"{_log('总观看时长: ', lang=self.config.language)}{watchHours}")
                # Make sure to come to the lolesports schedule page
                try:
                    getLolesportsWeb(self.driver)
                except Exception:
                    self.log.error(format_exc())
                    self.log.error(
                        _log("无法打开Lolesports网页，网络问题，将于3秒后退出...", lang=self.config.language))
                    print(_("无法打开Lolesports网页，网络问题，将于3秒后退出...",
                            color="red", lang=self.config.language))
                    sysQuit(self.driver, _log(
                        "无法打开Lolesports网页，网络问题，将于3秒后退出...", lang=self.config.language))
                # Whether the load is complete
                wait = WebDriverWait(self.driver, 20)
                wait.until(ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.results-label")))
                sleep(1)
                if len(matches) == 0:
                    self.log.info(_log("没有赛区正在直播", lang=self.config.language))
                    print(_("没有赛区正在直播", color="green", lang=self.config.language))
                # 1 match
                elif len(matches) == 1:
                    self.log.info(
                        f"{len(matches)} {_log('个赛区正在直播中', lang=self.config.language)}")
                    print(
                        f"{len(matches)} {_('个赛区正在直播中', color='green', lang=self.config.language)}")
                # multiple matches
                else:
                    self.log.info(
                        f"{len(matches)} {_log('赛区正在直播中', lang=self.config.language)}")
                    print(
                        f"{len(matches)} {_('赛区正在直播中', color='green', lang=self.config.language)}")
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
                    print(_("识别到距离比赛时间较长 检查间隔为1小时", color="green", lang=self.config.language))
                    self.log.info(_log("识别到距离比赛时间较长 检查间隔为1小时", lang=self.config.language))
                self.log.info(
                    f"{_log('下次检查在:', lang=self.config.language)} {(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                self.log.info(f"{'=' * 50}")
                print(
                    f"{_('下次检查在:', color='green', lang=self.config.language)} [cyan]{(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                if maxRunHours != -1:
                    print(
                        f"{_('预计结束程序时间:', color='green', lang=self.config.language)} [cyan]{time.strftime('%H:%M', time.localtime(endTimePoint))}")
                print(
                    f"[bold yellow]>_<"
                    f"{'=' * 27}"
                    f">_<"
                    f"{'=' * 27}"
                    f">_<[/bold yellow]"
                )
                sleep(newDelay)
            if time.time() >= endTimePoint and maxRunHours != -1 and self.config.platForm == "windows":
                self.log.info(_log("程序设定运行时长已到，将于60秒后关机,请及时做好准备工作", lang=self.config.language))
                print(_("程序设定运行时长已到，将于60秒后关机,请及时做好准备工作", color="yellow", lang=self.config.language))
                os.system("shutdown -s -t 60")

        except NoSuchWindowException:
            self.log.error(_log("对应窗口找不到", lang=self.config.language))
            print(_("对应窗口找不到", color="red", lang=self.config.language))
            self.log.error(format_exc())
            self.utils.errorNotify(_log("对应窗口找不到", lang=self.config.language))
            sysQuit(self.driver, _log("对应窗口找不到", lang=self.config.language))
        except Exception:
            self.log.error(_log("发生错误", lang=self.config.language))
            print(_("发生错误", color="red", lang=self.config.language))
            self.log.error(format_exc())
            self.utils.errorNotify(_log("发生错误", lang=self.config.language))
            sysQuit(self.driver, _log("发生错误", lang=self.config.language))

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
            self.log.error(_log("获取比赛列表失败", lang=self.config.language))
            print(_("获取比赛列表失败", color="red", lang=self.config.language))
            self.log.error(format_exc())
            return []

    def closeAllTabs(self):
        """
        Closes all open tabs about lolesports.
        """
        try:
            removeList = []
            self.driver.switch_to.new_window('tab')
            newTab1 = self.driver.current_window_handle
            sleep(1)
            self.driver.switch_to.new_window('tab')
            newTab2 = self.driver.current_window_handle
            sleep(1)
            for k in self.currentWindows.keys():
                self.driver.switch_to.window(self.currentWindows[k])
                sleep(1)
                self.driver.close()
                removeList.append(k)
                sleep(1)
            self.driver.switch_to.window(self.mainWindow)
            sleep(1)
            self.driver.close()
            self.mainWindow = newTab2
            self.driver.switch_to.window(self.rewardWindow)
            sleep(1)
            self.driver.close()
            self.rewardWindow = newTab1
            for handle in removeList:
                self.currentWindows.pop(handle, None)
            print(_("所有窗口已关闭", color="green", lang=self.config.language))
            self.log.info(_log("所有窗口已关闭", lang=self.config.language))
        except Exception:
            self.log.error(_log("关闭所有窗口时发生异常", lang=self.config.language))
            print(_("关闭所有窗口时发生异常", color="red", lang=self.config.language))
            self.utils.errorNotify(error=_log(
                "关闭所有窗口时发生异常", lang=self.config.language))
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
                        f"{match} {_log('比赛结束', lang=self.config.language)}")
                    print(
                        f"{match} {_('比赛结束', color='green', lang=self.config.language)}")
                    self.driver.close()
                    removeList.append(keys)
                    sleep(2)
                    self.driver.switch_to.window(self.mainWindow)
                    sleep(3)
                else:
                    if keys in self.OVERRIDES:
                        self.rewards.checkRewards("twitch", keys)
                    else:
                        self.rewards.checkRewards("youtube", keys)
            for keys in removeList:
                self.currentWindows.pop(keys, None)
            self.driver.switch_to.window(self.mainWindow)
        except Exception:
            print(_("关闭已结束的比赛时发生错误", color="red", lang=self.config.language))
            self.utils.errorNotify(error=_log(
                "关闭已结束的比赛时发生错误", lang=self.config.language))
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
                self.log.info(f"{skipName}{_log('比赛跳过', lang=self.config.language)}")
                print(f"{skipName}{_('比赛跳过', color='yellow', lang=self.config.language)}")
                continue

            self.driver.switch_to.new_window('tab')
            sleep(1)
            self.currentWindows[match] = self.driver.current_window_handle
            # Identified as a Twitch stream.
            if match in self.OVERRIDES:
                url = self.OVERRIDES[match]
                self.driver.get(url)
                if not self.rewards.checkRewards("twitch", url):
                    return
                if self.config.closeStream:
                    self.closeStream()
                else:
                    try:
                        if self.twitch.setTwitchQuality():
                            self.log.info(
                                _log("Twitch 160p清晰度设置成功", lang=self.config.language))
                            print(_("Twitch 160p清晰度设置成功",
                                    color="green", lang=self.config.language))
                        else:
                            self.log.error(
                                _log("Twitch 清晰度设置失败", lang=self.config.language))
                            print(_("Twitch 清晰度设置失败", color="red",
                                    lang=self.config.language))
                    except Exception:
                        self.log.error(
                            _log("无法设置 Twitch 清晰度.", lang=self.config.language))
                        print(_("无法设置 Twitch 清晰度.", color="red",
                                lang=self.config.language))
                        self.log.error(format_exc())
            # Identified as a YouTube stream.
            else:
                url = match
                self.driver.get(url)
                # It is convenient to add to overrides next time
                self.log.info(self.driver.current_url)
                self.youtube.checkYoutubeStream()
                # When rewards are not currently available, no need to set the quality
                if not self.rewards.checkRewards("youtube", url):
                    return
                # remove the YouTube stream
                if self.config.closeStream:
                    self.closeStream()
                else:
                    try:
                        if self.youtube.setYoutubeQuality():
                            self.log.info(
                                _log("Youtube 144p清晰度设置成功", lang=self.config.language))
                            print(_("Youtube 144p清晰度设置成功",
                                    color="green", lang=self.config.language))
                        else:
                            self.utils.debugScreen(self.driver, "youtube")
                            self.log.error(
                                _log("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者", lang=self.config.language))
                            print(_("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者", color="red",
                                    lang=self.config.language))
                    except Exception:
                        self.utils.debugScreen(self.driver, "youtube")
                        self.log.error(
                            _log("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者", lang=self.config.language))
                        print(_("无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者", color="red",
                                lang=self.config.language))
                        self.log.error(format_exc())
            sleep(4)

    def closeStream(self):
        """
        Close the current video stream by removing the video player element from the DOM.
        """
        try:
            self.driver.execute_script("""var data=document.querySelector('#video-player').remove()""")
        except Exception:
            self.log.error(_log("关闭视频流失败.", lang=self.config.language))
            print(_("关闭视频流失败.", color='red', lang=self.config.language))
            self.log.error(format_exc())
        else:
            self.log.info(_log("视频流关闭成功.", lang=self.config.language))
            print(_("视频流关闭成功.", color='green', lang=self.config.language))

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
            nextMatchMonth = nextMatchDayTime.split(" ")[0]
            nextMatchDay = int(nextMatchDayTime.split(" ")[1])
            nextMatchTime = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch > div > div.EventTime > div > span.hour").text
            try:
                nextMatchAMOrPM = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch > div > div.EventTime > div > span.hour ~ span.ampm").text
            except NoSuchElementException:
                nextMatchAMOrPM = ""
            nextMatchLeague = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch > div > div.league > div.name").text
            nextMatchBO = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch > div > div.league > div.strategy").text
            if nextMatchAMOrPM == "PM" and nextMatchTime != "12":
                nextMatchStartHour = int(nextMatchTime) + 12
            elif nextMatchAMOrPM == "AM" and nextMatchTime == "12":
                nextMatchStartHour = 0
            else:
                nextMatchStartHour = int(nextMatchTime)
            self.nextMatchHour = nextMatchStartHour
            self.nextMatchDay = nextMatchDay
            nowHour = int(time.localtime().tm_hour)
            nowMonth = time.strftime("%b", time.localtime())
            nowDay = int(time.strftime("%d", time.localtime()))
            if (nowMonth in nextMatchMonth and nowDay == nextMatchDay and nowHour > nextMatchStartHour) or \
                    (nowMonth not in nextMatchMonth and nowDay < nextMatchDay) or \
                    (nowMonth in nextMatchMonth and nowDay > nextMatchDay):
                nextMatchTime = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.EventTime > div > span.hour").text
                nextMatchAMOrPM = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.EventTime > div > span.hour ~ span.ampm").text
                nextMatchLeague = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.league > div.name").text
                nextMatchBO = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate + div.EventMatch ~ div.EventMatch > div > div.league > div.strategy").text
                print(f'{_("检查下一场比赛时 过滤失效的比赛", color="yellow", lang=self.config.language)} '
                      f'[yellow]{nextMatchLeague}')
                print(
                    f"{_('下一场比赛时间:', color='green', lang=self.config.language)} "
                    f"[cyan]{nextMatchTime}{nextMatchAMOrPM}[/cyan] | "
                    f"[magenta]{nextMatchLeague}[/magenta] | "
                    f"[blue]{nextMatchBO}[/blue]")
                self.nextMatchDay = None
            else:
                print(
                    f"{_('下一场比赛时间:', color='green', lang=self.config.language)} "
                    f"[cyan]{nextMatchDayTime}[/cyan] | "
                    f"[cyan]{nextMatchTime}{nextMatchAMOrPM}[/cyan] | "
                    f"[magenta]{nextMatchLeague}[/magenta] | "
                    f"[blue]{nextMatchBO}[/blue]")
        except Exception:
            self.log.error(_log("获取下一场比赛时间失败", lang=self.config.language))
            self.log.error(format_exc())
            print(_("获取下一场比赛时间失败", color="red", lang=self.config.language))

    def countDrops(self, isInit=False):
        """
        Counts the number of drops and the total watch hours.

        :param isInit: Whether it is the first time to enter the page
        :return: The number of drops and the total watch hours
        """
        if self.config.countDrops:
            try:
                self.driver.switch_to.window(self.rewardWindow)
                # The first time you enter the page, you do not need to refresh
                if isInit is False:
                    self.driver.refresh()
                wait = WebDriverWait(self.driver, 15)
                # Wait for the drop list to finish loading
                try:
                    wait.until(ec.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.name")))
                except TimeoutException:
                    # Special cases where there is no drop ---- new account
                    wait.until(ec.presence_of_element_located(
                        (By.XPATH, "//div[text()='NO DROPS YET']")))
                    totalWatchHours = self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div.stats > div:nth-child(2) > div.number").text
                    return 0, totalWatchHours
                dropLocale = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="div.name")
                dropNumber = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="div.dropCount")
                totalWatchHours = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.stats > div:nth-child(2) > div.number").text
                totalDropsNumber = 0
            except Exception:
                print(_("获取掉落数失败", color="red", lang=self.config.language))
                self.log.error(_log("获取掉落数失败", lang=self.config.language))
                self.log.error(format_exc())
                return -1, 0
            # Not the first run
            if not isInit:
                try:
                    dropNumberInfo = []
                    for i in range(0, len(dropLocale)):
                        # Prevent empty situations that sometimes appear for some reason
                        if dropNumber[i].text[:-6] == '':
                            continue
                        dropNumberNow = int(dropNumber[i].text[:-6])
                        dropLocaleNow = dropLocale[i].text
                        drops = dropNumberNow - int(self.dropsDict.get(dropLocaleNow, 0))
                        if drops > 0:
                            dropNumberInfo.append(
                                dropLocaleNow + ":" + str(dropNumberNow - self.dropsDict.get(dropLocaleNow, 0)))
                            dropsNeedNotify = drops - self.isNotified.get(dropLocaleNow, 0)
                            if dropsNeedNotify > 0:
                                self.driver.find_element(
                                    by=By.XPATH, value=f"//div[text()='{dropLocaleNow}']").click()
                                for j in range(1, dropsNeedNotify + 1):
                                    self.driver.find_element(
                                        by=By.CSS_SELECTOR, value=f"div.accordion-body > div > div:nth-child({j})").click()
                                    poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg = self.rewards.getNewDropInfo()
                                    if poweredByImg is not None:
                                        self.log.info(
                                            f"[{self.config.nickName}] BY {eventTitle} GET {dropItem} ON {dropLocaleNow} {unlockedDate}")
                                        print(
                                            f"[cyan][{self.config.nickName}][/cyan] "
                                            f"[blue]BY[/blue] {eventTitle} "
                                            f"[blue]GET[/blue] {dropItem} "
                                            f"[blue]ON[/blue] {dropLocaleNow} "
                                            f"[blue]{unlockedDate}")
                                        if self.config.desktopNotify:
                                            desktopNotify(
                                                poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg, dropLocaleNow)
                                        if self.config.connectorDropsUrl != "":
                                            self.rewards.notifyDrops(
                                                poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg, dropLocaleNow)
                                    sleep(3)
                                self.isNotified[dropLocaleNow] = self.isNotified.get(dropLocaleNow, 0) + dropsNeedNotify
                        totalDropsNumber = totalDropsNumber + dropNumberNow
                    if len(dropNumberInfo) != 0:
                        print(
                            f"{_('本次运行掉落详细:', color='green', lang=self.config.language)} {dropNumberInfo}")
                        self.log.info(
                            f"{_log('本次运行掉落详细:', lang=self.config.language)} {dropNumberInfo}")
                    return totalDropsNumber, totalWatchHours
                except Exception:
                    print(_("统计掉落失败", color="red", lang=self.config.language))
                    self.log.error(
                        _log("统计掉落失败", lang=self.config.language))
                    self.log.error(format_exc())
                    return -1, 0
            # First run
            else:
                try:
                    for i in range(0, len(dropLocale)):
                        if dropNumber[i].text[:-6] == '':
                            continue
                        self.dropsDict[dropLocale[i].text] = int(
                            dropNumber[i].text[:-6])
                        totalDropsNumber = totalDropsNumber + int(dropNumber[i].text[:-6])
                    return totalDropsNumber, totalWatchHours
                except Exception:
                    print(_("初始化掉落数失败", color="red",
                            lang=self.config.language))
                    self.log.error(
                        _log("初始化掉落数失败", lang=self.config.language))
                    self.log.error(format_exc())
                    return -1, 0
        else:
            return -1, 0

    def getRewardPage(self, newTab=False):
        """
        Get the rewards page in the browser and initialize the drop count.

        Args:
        - newTab (bool): A boolean flag to indicate whether to open the rewards page in a new tab (default: False).

        Raises:
        - Exception: If the function fails to get the rewards page or count the drops.
        """
        try:
            if newTab:
                self.driver.switch_to.new_window("tab")
            self.driver.get("https://lolesports.com/rewards")
            self.rewardWindow = self.driver.current_window_handle
            # Initialize drop count
            self.historyDrops, temp = self.countDrops(isInit=True)
        except Exception:
            print(_("检查掉落数失败", color="red", lang=self.config.language))
            self.log.error(_log("检查掉落数失败", lang=self.config.language))
            self.log.error(format_exc())

    def getSleepPeriod(self):
        """
        Get sleep period from config file
        """
        for period in self.config.sleepPeriod:
            if period == "":
                continue
            self.sleepBeginList.append(int(period.split("-")[0]))
            self.sleepEndList.append(int(period.split("-")[1]))
