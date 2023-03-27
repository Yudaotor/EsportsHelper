import traceback

import requests
from rich import print
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.Youtube import Youtube


class Match:

    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.rewards = Rewards(log=log, driver=driver, config=config)
        self.twitch = Twitch(driver=driver, log=log)
        self.youtube = Youtube(driver=driver, log=log)
        self.currentWindows = {}
        self.mainWindow = self.driver.current_window_handle
        self.OVERRIDES = {}
        try:
            remoteBestStreamsFile = requests.get("https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt")
            if remoteBestStreamsFile.status_code == 200:
                override = remoteBestStreamsFile.text.split(",")
                first = True
                for o in override:
                    temp = o.split("|")
                    if len(temp) == 2:
                        if first:
                            first = False
                        else:
                            temp[0] = temp[0][1:]
                        self.OVERRIDES[temp[0]] = temp[1]
        except Exception as ex:
            traceback.print_exc()
            print(f"[red]〒.〒 获取文件失败,请检查网络是否能连上github[/red]")
            input("按任意键退出")

    def watchMatches(self, delay):
        self.currentWindows = {}
        self.mainWindow = self.driver.current_window_handle
        while True:
            try:
                self.log.info("●_● 开始检查直播...")
                print(f"[green]●_● 开始检查直播...[/green]")
                self.driver.switch_to.window(self.mainWindow)
                isDrop, imgUrl, title = self.rewards.checkNewDrops()
                if isDrop:
                    self.log.info(f"ΩДΩ 发现新的掉落: {title}")
                    print(f"[blue]ΩДΩ 发现新的掉落: {title}[/blue]")
                    if self.config.connectorDropsUrl != "":
                        self.rewards.notifyDrops(imgUrl=imgUrl, title=title)
                time.sleep(3)
                try:
                    self.driver.get("https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
                except Exception as e:
                    self.driver.get("https://lolesports.com/schedule")
                time.sleep(5)
                liveMatches = self.getMatches()
                time.sleep(3)
                if len(liveMatches) == 0:
                    self.log.info("〒.〒 没有赛区正在直播")
                    print(f"[green]〒.〒 没有赛区正在直播[/green]")
                else:
                    self.log.info(f"ㅎ.ㅎ 现在有 {len(liveMatches)} 个赛区正在直播中")
                    print(f"[green]ㅎ.ㅎ 现在有 {len(liveMatches)} 个赛区正在直播中[/green]")

                self.closeTabs(liveMatches=liveMatches)

                self.openNewMatches(liveMatches=liveMatches, disWatchMatches=self.config.disWatchMatches)
                time.sleep(3)

                self.driver.switch_to.window(self.mainWindow)
                self.log.info(f"下一次检查在: {datetime.now() + timedelta(seconds=delay)}")
                self.log.debug("============================================")
                print(f"[green]下一次检查在: {(datetime.now() + timedelta(seconds=delay)).strftime('%m{m}%d{d} %H{h}%M{f}%S{s}').format(m='月',d='日',h='时',f='分',s='秒')}[/green]")
                print(f"[green]============================================[/green]")
                time.sleep(delay)
            except Exception as e:
                self.log.error("Q･Q 发生错误")
                print(f"[red]Q･Q 发生错误[/red]")
                traceback.print_exc()
                self.log.error(traceback.format_exc())

    def getMatches(self):
        try:
            matches = []
            elements = self.driver.find_elements(by=By.CSS_SELECTOR, value=".EventMatch .event.live")
            for element in elements:
                matches.append(element.get_attribute("href"))
            return matches
        except Exception as e:
            self.log.error("Q･Q 获取比赛列表失败")
            print(f"[red]Q･Q 获取比赛列表失败[/red]")
            traceback.print_exc()
            self.log.error(traceback.format_exc())
            return []

    def closeTabs(self, liveMatches):
        try:
            removeList = []
            for k in self.currentWindows.keys():
                self.driver.switch_to.window(self.currentWindows[k])
                if k not in liveMatches:
                    splitUrl = k.split('/')
                    if splitUrl[-2] != "live":
                        match = splitUrl[-2]
                    else:
                        match = splitUrl[-1]
                    self.log.info(f"̋0.0 {match} 比赛结束")
                    print(f"[yellow]̋0.0 {match} 比赛结束[/yellow]")
                    self.driver.close()
                    removeList.append(k)
                    self.driver.switch_to.window(self.mainWindow)
                    time.sleep(5)
                else:
                    self.rewards.checkRewards(k)
            for k in removeList:
                self.currentWindows.pop(k, None)
            self.driver.switch_to.window(self.mainWindow)
        except Exception as e:
            traceback.print_exc()
            self.log.error(traceback.format_exc())

    def openNewMatches(self, liveMatches, disWatchMatches):
        newLiveMatches = set(liveMatches) - set(self.currentWindows.keys())
        for match in newLiveMatches:

            flag = True
            for disMatch in disWatchMatches:
                if match.find(disMatch) != -1:
                    splitUrl = match.split('/')
                    if splitUrl[-2] != "live":
                        skipName = splitUrl[-2]
                    else:
                        skipName = splitUrl[-1]
                    self.log.debug(f"^▽^ {skipName}比赛跳过")
                    print(f"[yellow]^▽^ {skipName}比赛跳过")
                    flag = False
                    break
            if not flag:
                continue

            self.driver.switch_to.new_window('tab')
            time.sleep(1)
            self.currentWindows[match] = self.driver.current_window_handle
            if match in self.OVERRIDES:
                url = self.OVERRIDES[match]
                self.driver.get(url)
                if not self.rewards.checkRewards(url):
                    return
                try:
                    if self.twitch.setTwitchQuality():
                        self.log.info("≧-≦ Twitch 清晰度设置成功")
                        print("[green]≧-≦ Twitch 清晰度设置成功")
                    else:
                        self.log.critical("°D° Twitch 清晰度设置失败")
                        print("[red]°D° Twitch 清晰度设置失败")
                except Exception:
                    self.log.critical("°D° 无法设置 Twitch 清晰度.")
                    print("[red]°D° 无法设置 Twitch 清晰度.")
                    traceback.print_exc()
                    self.log.error(traceback.format_exc())
            else:
                url = match
                self.driver.get(url)
                try:
                    if self.youtube.setYoutubeQuality():
                        self.log.info("≧-≦ Youtube 清晰度设置成功")
                        print("[green]≧-≦ Youtube 清晰度设置成功")
                    else:
                        self.log.critical("°D° Youtube 清晰度设置失败")
                        print("[red]°D° Youtube 清晰度设置失败")
                    self.rewards.checkRewards(url)
                except Exception:
                    self.log.critical(f"°D° 无法设置 Youtube 清晰度.")
                    print("[red]°D° 无法设置 Youtube 清晰度.")
                    traceback.print_exc()
                    self.log.error(traceback.format_exc())
            time.sleep(5)
