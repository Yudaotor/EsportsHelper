import time
from datetime import datetime, timedelta
from random import randint
from time import sleep
from traceback import format_exc

from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.Utils import (Utils, _, _log, desktopNotify,
                                 downloadOverrideFile, getLolesportsWeb,
                                 getMatchName, sysQuit)
from EsportsHelper.Youtube import Youtube
from retrying import retry
from rich import print
from selenium.common import NoSuchElementException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class Match:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.utils = Utils(config=config)
        self.youtube = Youtube(driver=driver, log=log)
        self.rewards = Rewards(
            log=log, driver=driver, config=config, youtube=self.youtube, utils=self.utils)
        self.twitch = Twitch(driver=driver, log=log)
        self.currentWindows = {}
        self.rewardWindow = None
        self.mainWindow = self.driver.current_window_handle
        self.OVERRIDES = downloadOverrideFile()
        self.historyDrops = 0
        self.dropsDict = {}

    def watchMatches(self, delay, maxRunHours):
        try:
            self.currentWindows = {}
            self.mainWindow = self.driver.current_window_handle
            maxRunSecond = maxRunHours * 3600
            startTimePoint = time.time()
            endTimePoint = startTimePoint + maxRunSecond
            if self.config.countDrops:
                # 打开奖励页面
                try:
                    self.driver.switch_to.new_window('tab')
                    self.driver.get("https://lolesports.com/rewards")
                    self.rewardWindow = self.driver.current_window_handle
                    # 初始化掉落计数
                    self.historyDrops = self.countDrops(isInit=True)
                except Exception:
                    print(_("检查掉落数失败", color="red", lang=self.config.language))
                    self.log.error(_log("检查掉落数失败", lang=self.config.language))
                    self.log.error(format_exc())
            while maxRunHours < 0 or time.time() < endTimePoint:
                self.log.info(_log("●_● 开始检查...", lang=self.config.language))
                print(_("●_● 开始检查...", color="yellow", lang=self.config.language))
                dropsNumber = self.countDrops()
                if dropsNumber != 0:
                    print(f"{_('$_$ 本次运行掉落总和:', color='green', lang=self.config.language)}{dropsNumber - self.historyDrops} {_('生涯总掉落:', color='green', lang=self.config.language)}{dropsNumber}")
                    self.log.info(
                        f"{_log('$_$ 本次运行掉落总和:', lang=self.config.language)}{dropsNumber - self.historyDrops} {_log('生涯总掉落:', lang=self.config.language)}{dropsNumber}")
                self.driver.switch_to.window(self.mainWindow)
                isDrop, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg = self.rewards.checkNewDrops()
                if isDrop:
                    for i in range(len(poweredByImg)):
                        self.log.info(
                            f"ΩДΩ [{self.config.username}] BY {eventTitle[i]} GET {dropItem[i]} {unlockedDate[i]}")
                        print(
                            f"ΩДΩ [{self.config.username}] BY {eventTitle[i]} GET {dropItem[i]} {unlockedDate[i]}")
                        if self.config.desktopNotify:
                            desktopNotify(
                                poweredByImg[i], productImg[i], unlockedDate[i], eventTitle[i], dropItem[i], dropItemImg[i])
                        if self.config.connectorDropsUrl != "":
                            self.rewards.notifyDrops(
                                poweredByImg[i], productImg[i], eventTitle[i], unlockedDate[i], dropItem[i], dropItemImg[i])
                sleep(3)
                # 来到lolesports网页首页
                try:
                    getLolesportsWeb(self.driver)
                except Exception:
                    self.log.error(format_exc())
                    self.log.error(
                        _log("Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...", lang=self.config.language))
                    print(_("Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...",
                          color="red", lang=self.config.language))
                    sysQuit(self.driver, _log(
                        "Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...", lang=self.config.language))

                sleep(4)
                liveMatches = self.getMatchInfo()
                sleep(3)
                if len(liveMatches) == 0:
                    self.log.info(
                        _log("〒.〒 没有赛区正在直播", lang=self.config.language))
                    print(_("〒.〒 没有赛区正在直播", color="green",
                          lang=self.config.language))
                else:
                    self.log.info(
                        f"Q_P {len(liveMatches)} {_log('赛区正在直播中', lang=self.config.language)}")
                    print(
                        f"Q_P {len(liveMatches)} {_('赛区正在直播中', color='green', lang=self.config.language)}")
                # 关闭已经结束的赛区直播间
                self.closeFinishedTabs(liveMatches=liveMatches)
                # 开始观看新开始的直播
                self.startWatchNewMatches(
                    liveMatches=liveMatches, disWatchMatches=self.config.disWatchMatches)
                sleep(3)
                if self.config.sleepPeriod == "":
                    # 随机数，用于随机延迟
                    randomDelay = randint(int(delay * 0.08), int(delay * 0.15))
                    newDelay = randomDelay * 10
                else:
                    nowTime = int(time.localtime().tm_hour)
                    sleepBegin = int(self.config.sleepPeriod.split("-")[0])
                    sleepEnd = int(self.config.sleepPeriod.split("-")[1])
                    if sleepBegin <= nowTime < sleepEnd:
                        self.log.info(_log("处于休眠时间，检查时间间隔为1小时",
                                      lang=self.config.language))
                        print(_("处于休眠时间，检查时间间隔为1小时", color="green",
                              lang=self.config.language))
                        newDelay = 3600
                    else:
                        randomDelay = randint(
                            int(delay * 0.08), int(delay * 0.15))
                        newDelay = randomDelay * 10
                self.driver.switch_to.window(self.mainWindow)
                # 检查最近一个比赛的信息
                self.checkNextMatch()
                self.log.info(
                    f"{_log('下一次检查在:', lang=self.config.language)} {datetime.now() + timedelta(seconds=newDelay)}")
                self.log.info(
                    "==================================================")
                if self.config.language == "zh_CN":
                    print(
                        f"[green]下一次检查在: {(datetime.now() + timedelta(seconds=newDelay)).strftime('%m{m}%d{d} %H{h}%M{f}%S{s}').format(m='月',d='日',h='时',f='分',s='秒')}")
                elif self.config.language == "en_US":
                    print(
                        f"[green]Next check at: {(datetime.now() + timedelta(seconds=newDelay)).strftime('%m-%d %H:%M:%S')}")
                if maxRunHours != -1:
                    print(
                        f"{_('预计结束程序时间:', color='green', lang=self.config.language)} {time.strftime('%H:%M', time.localtime(endTimePoint))}")
                print(
                    f"[green]==================================================[/green]")
                sleep(newDelay)
        except NoSuchWindowException as e:
            self.log.error(_log("Q_Q 对应窗口找不到", lang=self.config.language))
            print(_("Q_Q 对应窗口找不到", color="red", lang=self.config.language))
            self.log.error(format_exc())
            self.utils.errorNotify(
                _log("Q_Q 对应窗口找不到", lang=self.config.language))
            sysQuit(self.driver, _log("Q_Q 对应窗口找不到", lang=self.config.language))
        except Exception as e:
            self.log.error(_log("Q_Q 发生错误", lang=self.config.language))
            print(_("Q_Q 发生错误", color="red", lang=self.config.language))
            self.log.error(format_exc())
            self.utils.errorNotify(_log("Q_Q 发生错误", lang=self.config.language))
            sysQuit(self.driver, _log("Q_Q 发生错误", lang=self.config.language))

    def getMatchInfo(self):
        try:
            matches = []
            if self.config.ignoreBroadCast:
                elements = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value=".EventMatch .event.live")
            else:
                elements = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value=".event.live")
            for element in elements:
                matches.append(element.get_attribute("href"))
            return matches
        except Exception:
            self.log.error(_log("Q_Q 获取比赛列表失败", lang=self.config.language))
            print(_("Q_Q 获取比赛列表失败", color="red", lang=self.config.language))
            self.log.error(format_exc())
            return []

    def closeFinishedTabs(self, liveMatches):
        try:
            removeList = []
            for k in self.currentWindows.keys():
                self.driver.switch_to.window(self.currentWindows[k])
                sleep(1)
                if k not in liveMatches:
                    match = getMatchName(k)
                    self.log.info(
                        f"0.0 {match} {_log('比赛结束', lang=self.config.language)}")
                    print(
                        f"0.0 {match} {_('比赛结束', color='green', lang=self.config.language)}")
                    self.driver.close()
                    removeList.append(k)
                    sleep(2)
                    self.driver.switch_to.window(self.mainWindow)
                    sleep(3)
                else:
                    if k in self.OVERRIDES:
                        self.rewards.checkRewards("twitch", k)
                    else:
                        self.rewards.checkRewards("youtube", k)
            for k in removeList:
                self.currentWindows.pop(k, None)
            self.driver.switch_to.window(self.mainWindow)
        except Exception as e:
            print(_("Q_Q 关闭已结束的比赛时发生错误", color="red", lang=self.config.language))
            self.utils.errorNotify(error=_log(
                "Q_Q 关闭已结束的比赛时发生错误", lang=self.config.language))
            self.log.error(format_exc())

    def startWatchNewMatches(self, liveMatches, disWatchMatches):
        newLiveMatches = set(liveMatches) - set(self.currentWindows.keys())
        for match in newLiveMatches:
            flag = True
            for disMatch in disWatchMatches:
                if match.find(disMatch) != -1:
                    skipName = getMatchName(match)
                    self.log.info(
                        f"(╯#-_-)╯ {skipName}{_log('比赛跳过', lang=self.config.language)}")
                    print(
                        f"(╯#-_-)╯ {skipName}{_('比赛跳过', color='yellow', lang=self.config.language)}")
                    flag = False
                    break
            if not flag:
                continue

            self.driver.switch_to.new_window('tab')
            sleep(1)
            self.currentWindows[match] = self.driver.current_window_handle
            # 判定为Twitch流
            if match in self.OVERRIDES:
                url = self.OVERRIDES[match]
                self.driver.get(url)
                if not self.rewards.checkRewards("twitch", url):
                    return
                if self.config.closeStream:
                    try:
                        self.driver.execute_script(
                            """var data=document.querySelector('#video-player').remove()""")
                    except Exception:
                        self.log.error(
                            _log("°D° 关闭 Twitch 流失败.", lang=self.config.language))
                        print(_("°D° 关闭 Twitch 流失败.", color="red",
                              lang=self.config.language))
                        self.log.error(format_exc())
                    else:
                        self.log.info(
                            _log(">_< Twitch 流关闭成功", lang=self.config.language))
                        print(_(">_< Twitch 流关闭成功", color="green",
                              lang=self.config.language))
                else:
                    try:
                        if self.twitch.setTwitchQuality():
                            self.log.info(
                                _log(">_< Twitch 160p清晰度设置成功", lang=self.config.language))
                            print(_(">_< Twitch 160p清晰度设置成功",
                                  color="green", lang=self.config.language))
                        else:
                            self.log.error(
                                _log("°D° Twitch 清晰度设置失败", lang=self.config.language))
                            print(_("°D° Twitch 清晰度设置失败", color="red",
                                  lang=self.config.language))
                    except Exception:
                        self.log.error(
                            _log("°D° 无法设置 Twitch 清晰度.", lang=self.config.language))
                        print(_("°D° 无法设置 Twitch 清晰度.", color="red",
                              lang=self.config.language))
                        self.log.error(format_exc())
            # 判定为Youtube流
            else:
                url = match
                self.driver.get(url)
                # 方便下次添加入overrides中
                self.log.info(self.driver.current_url)

                self.youtube.playYoutubeStream()
                if not self.rewards.checkRewards("youtube", url):
                    return
                # 关闭 Youtube 流
                if self.config.closeStream:
                    try:
                        self.driver.execute_script(
                            """var data=document.querySelector('#video-player').remove()""")
                    except Exception:
                        self.log.error(
                            _log("°D° 关闭 Youtube 流失败.", lang=self.config.language))
                        print(_("°D° 关闭 Youtube 流失败.", color="red",
                              lang=self.config.language))
                        self.log.error(format_exc())
                    else:
                        self.log.info(_log(">_< Youtube 流关闭成功",
                                      lang=self.config.language))
                        print(_(">_< Youtube 流关闭成功", color="green",
                              lang=self.config.language))
                else:
                    try:
                        if self.youtube.setYoutubeQuality():
                            self.log.info(
                                _log(">_< Youtube 144p清晰度设置成功", lang=self.config.language))
                            print(_(">_< Youtube 144p清晰度设置成功",
                                  color="green", lang=self.config.language))
                        else:
                            self.log.error(
                                _log("°D° Youtube 清晰度设置失败", lang=self.config.language))
                            print(_("°D° Youtube 清晰度设置失败", color="red",
                                  lang=self.config.language))
                    except Exception:
                        self.log.error(
                            _log("°D° 无法设置 Youtube 清晰度.", lang=self.config.language))
                        print(_("°D° 无法设置 Youtube 清晰度.", color="red",
                              lang=self.config.language))
                        self.log.error(format_exc())
            sleep(5)

    def checkNextMatch(self):
        try:
            nextMatchDayTime = self.driver.find_element(
                by=By.CSS_SELECTOR, value="div.divider.future + div.EventDate > div.date > span.monthday").text
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
            print(
                f"{_('下一场比赛时间:', color='green', lang=self.config.language)} [green]DATE {nextMatchDayTime}|TIME {nextMatchAMOrPM} {nextMatchTime} CLOCK|{nextMatchLeague} {nextMatchBO}[/green]")
        except Exception:
            self.log.error(_log("Q_Q 获取下一场比赛时间失败", lang=self.config.language))
            self.log.error(format_exc())
            print(_("Q_Q 获取下一场比赛时间失败", color="red", lang=self.config.language))

    def countDrops(self, isInit=False):
        if self.config.countDrops:
            try:
                self.driver.switch_to.window(self.rewardWindow)
                self.driver.refresh()
                wait = WebDriverWait(self.driver, 10)
                wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.name")))
                dropLocale = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="div.name")
                dropNumber = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="div.dropCount")
                sumNumber = 0
            except Exception:
                print(_("Q_Q 获取掉落数失败", color="red", lang=self.config.language))
                self.log.error(_log("Q_Q 获取掉落数失败", lang=self.config.language))
                self.log.error(format_exc())
                return 0
            # 不是第一次运行
            if not isInit:
                try:
                    dropNumberInfo = []
                    for i in range(0, len(dropLocale)):
                        if dropNumber[i].text[:-6] == '':
                            continue
                        dropNumberNow = int(dropNumber[i].text[:-6])
                        dropLocaleNow = dropLocale[i].text
                        if self.dropsDict.get(dropLocaleNow, 0) != dropNumberNow:
                            dropNumberInfo.append(
                                dropLocaleNow + ":" + str(dropNumberNow - self.dropsDict.get(dropLocaleNow, 0)))
                        sumNumber = sumNumber + dropNumberNow
                    if len(dropNumberInfo) != 0:
                        print(
                            f"{_('$_$ 本次运行掉落详细:', color='green', lang=self.config.language)} {dropNumberInfo}")
                        self.log.info(
                            f"{_log('$_$ 本次运行掉落详细:', lang=self.config.language)} {dropNumberInfo}")
                    return sumNumber
                except Exception:
                    print(_("QAQ 统计掉落失败", color="red", lang=self.config.language))
                    self.log.error(
                        _log("QAQ 统计掉落失败", lang=self.config.language))
                    self.log.error(format_exc())
                    return 0
            # 第一次运行
            else:
                try:
                    for i in range(0, len(dropLocale)):
                        self.dropsDict[dropLocale[i].text] = int(
                            dropNumber[i].text[:-6])
                        sumNumber = sumNumber + int(dropNumber[i].text[:-6])
                    return sumNumber
                except Exception:
                    print(_("QAQ 初始化掉落数失败", color="red",
                          lang=self.config.language))
                    self.log.error(
                        _log("QAQ 初始化掉落数失败", lang=self.config.language))
                    self.log.error(format_exc())
                    return 0
        else:
            return 0
