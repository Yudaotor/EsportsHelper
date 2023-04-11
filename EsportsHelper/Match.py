import time
from datetime import datetime, timedelta
from random import randint
from time import sleep
from traceback import format_exc
from rich import print
from selenium.common import NoSuchWindowException, NoSuchElementException
from selenium.webdriver.common.by import By
from retrying import retry
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.Utils import sysQuit, desktopNotify, downloadOverrideFile, Utils, getMatchName
from EsportsHelper.Youtube import Youtube


class Match:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.utils = Utils(config=config)
        self.youtube = Youtube(driver=driver, log=log)
        self.rewards = Rewards(log=log, driver=driver, config=config, youtube=self.youtube, utils=self.utils)
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
                    print(f"[red]检查掉落数失败[/red]")
                    self.log.error("检查掉落数失败")
                    self.log.error(format_exc())
            while maxRunHours < 0 or time.time() < endTimePoint:
                self.log.info("●_● 开始检查...")
                print(f"[green]●_● 开始检查...[/green]")
                dropsNumber = self.countDrops()
                if dropsNumber != 0:
                    print(f"[green]$_$ 本次运行掉落总和:{dropsNumber - self.historyDrops} 生涯总掉落:{dropsNumber}[/green]")
                    self.log.info(f"$_$ 本次运行掉落总和:{dropsNumber - self.historyDrops} 生涯总掉落:{dropsNumber}")
                self.driver.switch_to.window(self.mainWindow)
                isDrop, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg = self.rewards.checkNewDrops()
                if isDrop:
                    for i in range(len(poweredByImg)):
                        self.log.info(f"ΩДΩ [{self.config.username}]通过事件{eventTitle[i]} 获得{dropItem[i]} {unlockedDate[i]}")
                        print(f"ΩДΩ [{self.config.username}]通过事件{eventTitle[i]} 获得{dropItem[i]} {unlockedDate[i]}")
                        if self.config.desktopNotify:
                            desktopNotify(poweredByImg[i], productImg[i], unlockedDate[i], eventTitle[i], dropItem[i], dropItemImg[i])
                        if self.config.connectorDropsUrl != "":
                            self.rewards.notifyDrops(poweredByImg[i], productImg[i], eventTitle[i], unlockedDate[i], dropItem[i], dropItemImg[i])
                sleep(3)
                # 来到lolesports网页首页
                try:
                    self.getLolesportsWeb()
                except Exception as e:
                    self.log.error(format_exc())
                    self.log.error("Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...")
                    print(f"[red]Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...[/red]")
                    sysQuit(self.driver, "网络问题，将于3秒后退出...")

                sleep(4)
                liveMatches = self.getMatchInfo()
                sleep(3)
                if len(liveMatches) == 0:
                    self.log.info("〒.〒 没有赛区正在直播")
                    print(f"[green]〒.〒 没有赛区正在直播[/green]")
                else:
                    self.log.info(f"ㅎ.ㅎ 现在有 {len(liveMatches)} 个赛区正在直播中")
                    print(
                        f"[green]ㅎ.ㅎ 现在有 {len(liveMatches)} 个赛区正在直播中[/green]")
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
                        self.log.info("处于休眠时间，检查时间间隔为1小时")
                        print(f"[green]处于休眠时间，检查时间间隔为1小时[/green]")
                        newDelay = 3600
                    else:
                        randomDelay = randint(int(delay * 0.08), int(delay * 0.15))
                        newDelay = randomDelay * 10
                self.driver.switch_to.window(self.mainWindow)
                # 检查最近一个比赛的信息
                self.checkNextMatch()
                self.log.info(
                    f"下一次检查在: {datetime.now() + timedelta(seconds=newDelay)}")
                self.log.debug("==================================================")
                print(
                    f"[green]下一次检查在: {(datetime.now() + timedelta(seconds=newDelay)).strftime('%m{m}%d{d} %H{h}%M{f}%S{s}').format(m='月',d='日',h='时',f='分',s='秒')}[/green]")
                if maxRunHours != -1:
                    print(f"[green]预计结束程序时间: {time.strftime('%H:%M', time.localtime(endTimePoint))} [/green]")
                print(f"[green]==================================================[/green]")
                sleep(newDelay)
        except NoSuchWindowException as e:
            self.log.error("Q_Q 对应窗口找不到")
            print(f"[red]Q_Q 对应窗口找不到[/red]")
            self.log.error(format_exc())
            self.utils.errorNotify("对应窗口找不到")
            sysQuit(self.driver, "对应窗口找不到")
        except Exception as e:
            self.log.error("Q_Q 发生错误")
            print(f"[red]Q_Q 发生错误[/red]")
            self.log.error(format_exc())
            self.utils.errorNotify("发生错误")
            sysQuit(self.driver, "发生错误")

    def getMatchInfo(self):
        try:
            matches = []
            elements = self.driver.find_elements(
                by=By.CSS_SELECTOR, value=".EventMatch .event.live")
            for element in elements:
                matches.append(element.get_attribute("href"))
            return matches
        except Exception as e:
            self.log.error("Q_Q 获取比赛列表失败")
            print(f"[red]Q_Q 获取比赛列表失败[/red]")
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
                    self.log.info(f"0.0 {match} 比赛结束")
                    print(f"[green]0.0 {match} 比赛结束[/green]")
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
            print(f"[red]Q_Q 关闭已结束的比赛时发生错误[/red]")
            self.utils.errorNotify(e="Q_Q 关闭已结束的比赛时发生错误")
            self.log.error(format_exc())

    def startWatchNewMatches(self, liveMatches, disWatchMatches):
        newLiveMatches = set(liveMatches) - set(self.currentWindows.keys())
        for match in newLiveMatches:
            flag = True
            for disMatch in disWatchMatches:
                if match.find(disMatch) != -1:
                    skipName = getMatchName(match)
                    self.log.info(f"(╯#-_-)╯ {skipName}比赛跳过")
                    print(f"[yellow](╯#-_-)╯ {skipName}比赛跳过")
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
                        self.driver.execute_script("""var data=document.querySelector('#video-player').remove()""")
                    except Exception:
                        self.log.error("°D° 关闭 Twitch 流失败.")
                        print("[red]°D° 关闭 Twitch 流失败.")
                        self.log.error(format_exc())
                    else:
                        self.log.info(">_< Twitch 流关闭成功")
                        print("[green]>_< Twitch 流关闭成功")
                else:
                    try:
                        if self.twitch.setTwitchQuality():
                            self.log.info(">_< Twitch 160p清晰度设置成功")
                            print("[green]>_< Twitch 160p清晰度设置成功")
                        else:
                            self.log.error("°D° Twitch 清晰度设置失败")
                            print("[red]°D° Twitch 清晰度设置失败")
                    except Exception:
                        self.log.error("°D° 无法设置 Twitch 清晰度.")
                        print("[red]°D° 无法设置 Twitch 清晰度.")
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
                        self.driver.execute_script("""var data=document.querySelector('#video-player').remove()""")
                    except Exception:
                        self.log.error("°D° 关闭 Youtube 流失败.")
                        print("[red]°D° 关闭 Youtube 流失败.")
                        self.log.error(format_exc())
                    else:
                        self.log.info(">_< Youtube 流关闭成功")
                        print("[green]>_< Youtube 流关闭成功")
                else:
                    try:
                        if self.youtube.setYoutubeQuality():
                            self.log.info(">_< Youtube 144p清晰度设置成功")
                            print("[green]>_< Youtube 144p清晰度设置成功")
                        else:
                            self.log.error("°D° Youtube 清晰度设置失败")
                            print("[red]°D° Youtube 清晰度设置失败")
                    except Exception:
                        self.log.error(f"°D° 无法设置 Youtube 清晰度.")
                        print("[red]°D° 无法设置 Youtube 清晰度.")
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
            print(f"[green]下一场比赛时间: 日期{nextMatchDayTime} 时间{nextMatchAMOrPM} {nextMatchTime}时 赛区{nextMatchLeague} {nextMatchBO}[/green]")
        except Exception:
            self.log.error("Q_Q 获取下一场比赛时间失败")
            self.log.error(format_exc())
            print(f"[red]Q_Q 获取下一场比赛时间失败[/red]")

    # 重复尝试获取网页最多4次，等待时间以2分钟为基数，每次递增2分钟
    @retry(stop_max_attempt_number=4, wait_incrementing_increment=120000, wait_incrementing_start=120000)
    def getLolesportsWeb(self):
        try:
            self.driver.get(
                "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
        except Exception:
            print("[red]Q_Q 获取Lolesports网页失败,重试中...[/red]")
            self.log.error("Q_Q 获取Lolesports网页失败,重试中...")
            self.driver.get(
                "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")

    def countDrops(self, isInit=False):
        if self.config.countDrops:
            try:
                self.driver.switch_to.window(self.rewardWindow)
                self.driver.refresh()
                wait = WebDriverWait(self.driver, 10)
                wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.name")))
                dropLocale = self.driver.find_elements(by=By.CSS_SELECTOR, value="div.name")
                dropNumber = self.driver.find_elements(by=By.CSS_SELECTOR, value="div.dropCount")
                sumNumber = 0
            except Exception:
                print("[red]Q_Q 获取掉落数失败[/red]")
                self.log.error("Q_Q 获取掉落数失败")
                self.log.error(format_exc())
                return 0
            # 不是第一次运行
            if not isInit:
                try:
                    dropNumberInfo = []
                    for i in range(0, len(dropLocale)):
                        if self.dropsDict.get(dropLocale[i].text, 0) != int(dropNumber[i].text[:-6]):
                            dropNumberInfo.append(dropLocale[i].text + ":" + str(int(dropNumber[i].text[:-6]) - self.dropsDict.get(dropLocale[i].text, 0)))
                        sumNumber = sumNumber + int(dropNumber[i].text[:-6])
                    if len(dropNumberInfo) != 0:
                        print(f"[green]$_$ 本次运行掉落详细: {dropNumberInfo}[/green]")
                        self.log.info(f"本次运行掉落详细: {dropNumberInfo}")
                    return sumNumber
                except Exception:
                    print("[red]눈_눈 统计掉落失败[/red]")
                    self.log.error("눈_눈 统计掉落失败")
                    self.log.error(format_exc())
                    return 0
            # 第一次运行
            else:
                try:
                    for i in range(0, len(dropLocale)):
                        self.dropsDict[dropLocale[i].text] = int(dropNumber[i].text[:-6])
                        sumNumber = sumNumber + int(dropNumber[i].text[:-6])
                    return sumNumber
                except Exception:
                    print("[red]눈_눈 初始化掉落数失败[/red]")
                    self.log.error("눈_눈 初始化掉落数失败")
                    self.log.error(format_exc())
                    return 0
        else:
            return 0
