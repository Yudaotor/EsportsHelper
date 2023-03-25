import traceback
from rich import print
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException
from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.Youtube import Youtube


class Match:
    OVERRIDES = {
        "https://lolesports.com/live/lck_challengers_league": "https://lolesports.com/live/lck_challengers_league/lckcl",
        "https://lolesports.com/live/lpl": "https://lolesports.com/live/lpl/lpl",
        "https://lolesports.com/live/lck": "https://lolesports.com/live/lck/lck",
        "https://lolesports.com/live/lec": "https://lolesports.com/live/lec/lec",
        "https://lolesports.com/live/lcs": "https://lolesports.com/live/lcs/lcs",
        "https://lolesports.com/live/lco": "https://lolesports.com/live/lco/lco",
        "https://lolesports.com/live/cblol_academy": "https://lolesports.com/live/cblol_academy/cblol",
        "https://lolesports.com/live/cblol": "https://lolesports.com/live/cblol/cblol",
        "https://lolesports.com/live/lla": "https://lolesports.com/live/lla/lla",
        "https://lolesports.com/live/ljl-japan/ljl": "https://lolesports.com/live/ljl-japan/riotgamesjp",
        "https://lolesports.com/live/ljl-japan": "https://lolesports.com/live/ljl-japan/riotgamesjp",
        "https://lolesports.com/live/turkiye-sampiyonluk-ligi": "https://lolesports.com/live/turkiye-sampiyonluk-ligi/riotgamesturkish",
        "https://lolesports.com/live/cblol-brazil": "https://lolesports.com/live/cblol-brazil/cblol",
        "https://lolesports.com/live/pcs/lXLbvl3T_lc": "https://lolesports.com/live/pcs/lolpacific",
        "https://lolesports.com/live/ljl_academy/ljl": "https://lolesports.com/live/ljl_academy/riotgamesjp",
        "https://lolesports.com/live/european-masters": "https://lolesports.com/live/european-masters/EUMasters",
        "https://lolesports.com/live/worlds": "https://lolesports.com/live/worlds/riotgames",
        "https://lolesports.com/live/honor_division": "https://lolesports.com/live/honor_division/lvpmexlol",
        "https://lolesports.com/live/volcano_discover_league": "https://lolesports.com/live/volcano_discover_league/lvpecuador",
        "https://lolesports.com/live/pcs": "https://lolesports.com/live/pcs/lolpacific",
        "https://lolesports.com/live/hitpoint_masters": "https://lolesports.com/live/hitpoint_masters/hitpointcz",
    }

    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.rewards = Rewards(log=log, driver=driver, config=config)
        self.twitch = Twitch(driver=driver)
        self.currentWindows = {}
        self.originalWindow = self.driver.current_window_handle
        self.youtube = Youtube(driver=driver)

    def watchForMatches(self, delay):
        self.currentWindows = {}
        self.originalWindow = self.driver.current_window_handle
        while True:
            try:
                self.driver.switch_to.window(self.originalWindow)
                time.sleep(3)
                self.driver.get("https://lolesports.com/schedule")
                time.sleep(5)
                liveMatches = self.getLiveMatches()
                self.log.info(f"现在有 {len(liveMatches)} 场比赛正在直播中")
                print(f"[green]现在有 {len(liveMatches)} 场比赛正在直播中[/green]")
                self.closeFinishedMatches(liveMatches=liveMatches)
                self.openNewMatches(liveMatches=liveMatches, disWatchMatches=self.config.disWatchMatches)
                time.sleep(3)
                self.driver.switch_to.window(self.originalWindow)
                self.log.info(f"下一次检查在: {datetime.now() + timedelta(seconds=delay)}")
                self.log.debug("============================================")
                print(f"[green]下一次检查在: {datetime.now() + timedelta(seconds=delay)}[/green]")
                print(f"[green]============================================[/green]")
                time.sleep(delay)
            except Exception as e:
                self.log.error("发生错误")
                print(f"[red]发生错误[/red]")
                traceback.print_exc()

    def getLiveMatches(self):
        try:
            matches = []
            elements = self.driver.find_elements(by=By.CSS_SELECTOR, value=".EventMatch .event.live")
            for element in elements:
                matches.append(element.get_attribute("href"))
            return matches
        except Exception as e:
            self.log.error("获取比赛列表失败")
            print(f"[red]获取比赛列表失败[/red]")
            traceback.print_exc()
            return []

    def closeFinishedMatches(self, liveMatches):
        toRemove = []
        for k in self.currentWindows.keys():
            self.driver.switch_to.window(self.currentWindows[k])
            if k not in liveMatches:
                self.log.info(f"{k} 比赛结束")
                print(f"[green]{k} 比赛结束[/green]")
                self.driver.close()
                toRemove.append(k)
                self.driver.switch_to.window(self.originalWindow)
                time.sleep(5)
            else:
                self.rewards.checkRewards(k)
        for k in toRemove:
            self.currentWindows.pop(k, None)
        self.driver.switch_to.window(self.originalWindow)

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
                    self.log.debug(f"{skipName}比赛跳过")
                    print(f"[yellow]{skipName}比赛跳过")
                    flag = False
                    break
            if not flag:
                continue
            self.driver.switch_to.new_window('tab')
            time.sleep(2)
            self.currentWindows[match] = self.driver.current_window_handle
            if match in self.OVERRIDES:
                url = self.OVERRIDES[match]
                self.driver.get(url)
                self.rewards.checkRewards(url)
                try:
                    self.twitch.setTwitchQuality()
                    self.log.info("Twitch 清晰度设置成功")
                    print("[green]Twitch 清晰度设置成功")
                except TimeoutException:
                    self.log.critical("无法设置 Twitch 清晰度. 这场比赛是在 Twitch 上吗?")
                    print("[red]无法设置 Twitch 清晰度. 这场比赛是在 Twitch 上吗?")
            else:
                url = match
                self.driver.get(url)
                try:
                    self.youtube.setYoutubeQuality()
                    self.rewards.checkRewards(url)
                    self.log.info("Youtube 清晰度设置成功")
                    print("[green]Youtube 清晰度设置成功")
                except TimeoutException:
                    self.log.critical(f"无法设置 Youtube 清晰度. 这场比赛是在 Youtube 上吗?")
                    print("[red]无法设置 Youtube 清晰度. 这场比赛是在 Youtube 上吗?")
            time.sleep(5)
