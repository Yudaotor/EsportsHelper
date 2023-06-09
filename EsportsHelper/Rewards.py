from time import sleep
from traceback import format_exc
from selenium import webdriver
import requests
from EsportsHelper.Utils import getMatchName, desktopNotify, checkRewardPage, getMatchTeams
from rich import print
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from EsportsHelper.Config import config
from EsportsHelper.Logger import log
from EsportsHelper.I18n import i18n
_ = i18n.getText
_log = i18n.getLog


class Rewards:
    def __init__(self, driver, youtube, utils, twitch) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.youtube = youtube
        self.utils = utils
        self.twitch = twitch
        self.dropsDict = {}
        self.isNotified = {}
        self.historyDrops = -1
        self.totalWatchHours = -1
        self.wait = WebDriverWait(self.driver, 30)

    def checkRewards(self, stream: str):
        """
        Checks if the reward mark exists on the current page.
        """
        try:
            # Check if the reward mark exists
            try:
                self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div[class=status-summary] g")))
            except Exception:
                self.log.error(format_exc())
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
                self.utils.debugScreen(self.driver, "vods")
                return 0

        except Exception:
            self.log.error(_log("检测奖励标识失败"))
            self.log.error(format_exc())
            self.utils.debugScreen(self.driver, "reward")

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
        teams = _log("出错, 未知")
        viewerNumber = _log("出错, 未知")
        for i in range(retryTimes):
            flag = self.checkRewards(stream=stream)
            if flag == 1 and self.config.closeStream is False:
                try:
                    if stream == "twitch":
                        frameLocator = (By.CSS_SELECTOR, "iframe[title=Twitch]")
                        self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))
                        teamLocator = (By.CSS_SELECTOR, "p[data-test-selector=stream-info-card-component__subtitle]")
                        teamsElement = self.wait.until(ec.presence_of_element_located(teamLocator))
                        teams = teamsElement.text
                        retryTeamsTimes = 6
                        while not teams and retryTeamsTimes > 0:
                            retryTeamsTimes -= 1
                            self.utils.debugScreen(self.driver, "teams")
                            self.driver.switch_to.default_content()
                            self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))
                            webdriver.ActionChains(self.driver).move_to_element(teamsElement).perform()
                            teams = self.wait.until(ec.presence_of_element_located(teamLocator)).text
                            self.log.warning(_log("获取队伍信息重试中..."))
                            sleep(5)

                        peopleLocator = (By.CSS_SELECTOR, "p[data-test-selector=stream-info-card-component__description]")
                        viewerInfoElement = self.wait.until(ec.presence_of_element_located(peopleLocator))
                        viewerInfo = viewerInfoElement.text
                        retryViewerTimes = 6
                        while not viewerInfo and retryViewerTimes > 0:
                            retryViewerTimes -= 1
                            self.utils.debugScreen(self.driver, "viewerNumber")
                            self.driver.switch_to.default_content()
                            self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))
                            webdriver.ActionChains(self.driver).move_to_element(viewerInfoElement).perform()
                            viewerInfo = self.wait.until(ec.presence_of_element_located(peopleLocator)).text
                            self.log.warning(_log("获取观看人数信息重试中..."))
                            sleep(5)

                        viewerNumberFlag = True
                        for num in viewerInfo:
                            if num.isdigit() and viewerNumberFlag:
                                viewerNumber = "" + num
                                viewerNumberFlag = False
                                continue
                            if num.isdigit():
                                viewerNumber += num
                        self.driver.switch_to.default_content()

                    elif stream == "youtube":
                        frameLocator = (By.ID, "video-player-youtube")
                        self.wait.until(ec.frame_to_be_available_and_switch_to_it(frameLocator))
                        iframeTitle = self.driver.execute_script("return document.title;")
                        teams = iframeTitle.strip() if iframeTitle else _log("出错, 未知")
                        self.driver.switch_to.default_content()
                    teams = getMatchTeams(teams)

                except Exception:
                    self.driver.switch_to.default_content()
                    self.log.error(format_exc())
                if stream == "twitch":
                    if self.twitch.checkTwitchStream() is False:
                        self.driver.refresh()
                        sleep(10)
                        self.twitch.setTwitchQuality()
                        self.twitch.checkTwitchStream()
                    self.log.info(
                        f"{match} {_log('正常观看 可获取奖励')} "
                        f"{_log('标题: ')}"
                        f"{teams} "
                        f"{_log('观看人数: ')}{viewerNumber}")
                    print(
                        f"[bold magenta]{match}[/bold magenta] {_('正常观看 可获取奖励', color='green')} ")
                    print(
                        f"--{_('标题: ', color='bold yellow')}"
                        f"[bold green]{teams}[/bold green]"
                    )
                    print(f"--{_('观看人数: ', 'bold yellow')}{viewerNumber}")
                elif stream == "youtube":
                    if self.youtube.checkYoutubeStream() is False:
                        self.driver.refresh()
                        sleep(10)
                        self.youtube.setYoutubeQuality()
                        self.youtube.checkYoutubeStream()
                    self.log.info(
                        f"{match} {_log('正常观看 可获取奖励')} "
                        f"{_log('标题: ')}"
                        f"{teams}")
                    print(
                        f"[bold magenta]{match}[/bold magenta] "
                        f"{_('正常观看 可获取奖励', color='green')} ")
                    print(
                        f"--{_('标题: ', color='bold yellow')}"
                        f"[bold green]{teams}[/bold green]")

                return True
            elif flag == 1 and self.config.closeStream is True:
                self.log.info(
                    f"{match} {_log('正常观看 可获取奖励')} ")
                print(f"[bold magenta]{match}[/bold magenta] "
                      f"{_('正常观看 可获取奖励', color='green')} ")
                return True
            elif flag == 0:
                times = 3
                while times > 0:
                    self.driver.get(url)
                    times -= 1
                    sleep(5)
                    self.utils.debugScreen(self.driver, "afterRefresh")
                    if self.checkRewards(stream=stream) == 1 and self.config.closeStream is False:
                        if stream == "twitch":
                            self.twitch.setTwitchQuality()
                        elif stream == "youtube":
                            self.youtube.setYoutubeQuality()
                        self.log.info(
                            f"{match} {_log('正常观看 可获取奖励')} ")
                        print(f"[bold magenta]{match}[/bold magenta] "
                              f"{_('正常观看 可获取奖励', color='green')} ")
                        self.utils.debugScreen(self.driver, "afterVods")
                        return True
                    elif self.checkRewards(stream=stream) == 1 and self.config.closeStream is True:
                        self.log.info(
                            f"{match} {_log('比赛结束 等待关闭')} ")
                        print(f"[bold magenta]{match}[/bold magenta] "
                              f"{_('比赛结束 等待关闭', color='yellow')} ")
                        self.utils.debugScreen(self.driver, "afterVods")
                        return True
                    elif self.checkRewards(stream=stream) == 0:
                        self.utils.debugScreen(self.driver, "afterVods")
                        continue
                self.log.info(
                    f"{match} {_log('比赛结束 等待关闭')} ")
                print(f"[bold magenta]{match}[/bold magenta] "
                      f"{_('比赛结束 等待关闭', color='yellow')} ")
                return True
            elif flag == -1:
                if i != retryTimes - 1:
                    self.utils.debugScreen(self.driver, "rewardFailed")
                    self.log.warning(f"{match} {_log('观看异常 重试中...')}")
                    print(f"[bold magenta]{match}[/bold magenta] "
                          f"{_('观看异常 重试中...', color='yellow')}")
                    sleep((i + 1) * 30)
                    self.driver.refresh()
                    sleep(10)
                    if stream == "youtube":
                        if self.youtube.checkYoutubeStream() is False:
                            self.driver.refresh()
                            sleep(10)
                            self.youtube.setYoutubeQuality()
                            self.youtube.checkYoutubeStream()
                    if stream == "twitch":
                        if self.twitch.checkTwitchStream() is False:
                            self.driver.refresh()
                            sleep(10)
                            self.twitch.setTwitchQuality()
                            self.twitch.checkTwitchStream()
                else:
                    self.log.error(
                        f"{match} {_log('观看异常')}")
                    print(
                        f"[bold magenta]{match}[/bold magenta] "
                        f"{_('观看异常', color='red')}")
                    self.utils.errorNotify(
                        f"{match} {_log('观看异常')}")
                    return False

    def getNewDropInfo(self):
        """
        Gets the information of the new drop.
        Returns a tuple containing the following elements:
            poweredByImg (str or None): The URL of the image of the sponsor of the drop, or None if not found.
            productImg (str or None): The URL of the image of the product being dropped, or None if not found.
            eventTitle (str or None): The title of the event associated with the drop, or None if not found.
            unlockedDate (str or None): The date and time when the drop will be unlocked, or None if not found.
            dropItem (str or None): The name of the item being dropped, or None if not found.
            dropItemImg (str or None): The URL of the image of the item being dropped, or None if not found.

        """
        try:
            # Wait for the drop info to be available
            self.wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div[class=product-image] > img[class=img]")))
            try:
                poweredByImg = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div[class=sponsor-image] > img[class=img]").get_attribute("src")
            except Exception:
                poweredByImg = ""
            try:
                productImg = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div[class=product-image] > img[class=img]").get_attribute("src")
            except Exception:
                productImg = ""
            try:
                eventTitle = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div.title.short").text
            except Exception:
                try:
                    eventTitle = self.driver.find_element(
                        by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div.title.long").text
                except Exception:
                    eventTitle = ""
            try:
                dropItem = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div[class=reward] > div[class=wrapper] > div[class=title]").text
            except Exception:
                dropItem = ""
            try:
                unlockedDate = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div.RewardsDropsOverlay > div.content > div.RewardsDropsCard > div > div.unlocked-date").text
            except Exception:
                unlockedDate = ""
            try:
                dropItemImg = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="div[class=reward] > div[class=image] > img[class=img]").get_attribute("src")
            except Exception:
                dropItemImg = ""
            try:
                closeButton = self.wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.RewardsDropsOverlay > div.close")))
            except Exception:
                closeButton = self.wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.stats > div:nth-child(2) > div.number")))
            closeButton.click()
            return poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg
        except Exception:
            self.log.error(_log("检查掉落失败"))
            self.log.error(format_exc())
            print(_("检查掉落失败", color="red"))
            return None, None, None, None, None, None

    def notifyDrops(self, poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg, dropRegion) -> None:
        """
            Sends a notification message about a drop obtained through a certain event to a configured webhook.

            Args:
                poweredByImg (str): The URL of the image of the platform logo that powered the drop.
                productImg (str): The URL of the image of the product that was dropped.
                eventTitle (str): The title of the event that the drop was obtained through.
                unlockedDate (str): The date and time at which the drop was unlocked.
                dropItem (str): The name of the item that was dropped.
                dropItemImg (str): The URL of the image of the item that was dropped.
                dropRegion (str): The locale where the event took place.

            Returns:
                None. This function only sends a notification message.

            Raises:
                Exception: If there was an error sending the notification message.
            """
        if self.config.notifyType in ["all", "drops"]:
            try:
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Drop掉落提醒",
                            "title": f"[{self.config.nickName}]在{dropRegion} 通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                            "picUrl": f"{dropItemImg}",
                            "messageUrl": "https://lolesports.com/rewards"
                        }
                    }
                    s.post(self.config.connectorDropsUrl, json=data)
                    sleep(5)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    field0 = {
                        "name": "Account",
                        "value": f"{self.config.nickName}",
                        "inline": True
                    }
                    field1 = {
                        "name": "Event",
                        "value": f"{eventTitle}",
                        "inline": True
                    }
                    field2 = {
                        "name": "Reward",
                        "value": f"{dropItem}",
                        "inline": True
                    }
                    field4 = {
                        "name": "Date",
                        "value": f"{unlockedDate}",
                        "inline": True
                    }
                    field5 = {
                        "name": "Region",
                        "value": f"{dropRegion}",
                        "inline": True
                    }
                    fieldNone = {
                        "name": "",
                        "value": "",
                        "inline": True
                    }
                    embed = {
                        "title": "Drop!",
                        "image": {"url": f"{productImg}"},
                        "thumbnail": {"url": f"{dropItemImg}"},
                        "fields": [field0, field1, fieldNone, field2, field4, field5, fieldNone],
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    sleep(5)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"[{self.config.nickName}]在{dropRegion} "
                                f"通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    sleep(5)
                else:
                    params = {
                        "text": f"[{self.config.nickName}]在{dropRegion} "
                                f"通过事件{eventTitle} 获得{dropItem} {unlockedDate}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                        "Content-type": "application/json"}, json=params)
                    sleep(5)
                self.log.info(_log("掉落提醒成功"))
            except Exception:
                self.log.error(_log("掉落提醒失败"))
                self.log.error(format_exc())
                print(_("掉落提醒失败", color="red"))

    def countDrops(self, rewardWindow, isInit=False):
        """
        Counts the number of drops and the total watch hours.

        :param rewardWindow:
        :param isInit: Whether it is the first time to enter the page
        """
        if self.config.countDrops:
            try:
                if isInit is True:
                    print(f'{_("初始化掉落数", color="green")}')
                    self.log.info(_log("初始化掉落数"))
                else:
                    print(f'--{_("检查掉落数...", color="green")}')
                    self.log.info(_log("检查掉落数..."))
                self.driver.switch_to.window(rewardWindow)
                # The first time you enter the page, you do not need to refresh
                if isInit is False:
                    self.driver.refresh()
                # Wait for the drop list to finish loading
                try:
                    checkRewardPage(self.driver)
                except Exception:
                    self.log.error(format_exc())
                    return -1, ""
                dropRegion = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="div.name")
                dropNumber = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="div.dropCount")
                totalWatchHours = self.wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.stats > div:nth-child(2) > div.number"))).text
                totalDropsNumber = 0
            except Exception:
                print(_("获取掉落数失败", color="red"))
                self.log.error(_log("获取掉落数失败"))
                self.log.error(format_exc())
                return -1, ""
            # Not the first run
            if not isInit:
                try:
                    dropNumberInfo = []

                    for i in range(0, len(dropRegion)):
                        # Prevent empty situations that sometimes appear for some reason
                        if dropNumber[i].text[:-6] == '':
                            continue
                        dropNumberNow = int(dropNumber[i].text[:-6])
                        dropRegionNow = dropRegion[i].text
                        drops = dropNumberNow - int(self.dropsDict.get(dropRegionNow, 0))
                        if drops > 0 and totalWatchHours != -1:
                            dropNumberInfo.append(
                                dropRegionNow + ":" + str(dropNumberNow - self.dropsDict.get(dropRegionNow, 0)))
                            dropsNeedNotify = drops - self.isNotified.get(dropRegionNow, 0)
                            if dropsNeedNotify > 0:
                                regionName = self.wait.until(ec.presence_of_element_located(
                                    (By.XPATH, f"//div[text()='{dropRegionNow}']")))
                                self.driver.execute_script("arguments[0].click();", regionName)
                                for j in range(dropsNeedNotify, 0, -1):
                                    dropItem = self.wait.until(ec.presence_of_element_located(
                                        (By.CSS_SELECTOR, f"div.accordion-body > div > div:nth-child({j})")))
                                    webdriver.ActionChains(self.driver).move_to_element(dropItem).click(dropItem).perform()
                                    poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg = self.getNewDropInfo()
                                    if poweredByImg is not None:
                                        self.log.info(
                                            f"<{self.config.nickName}>|BY| {eventTitle} |GET| {dropItem} |ON| {dropRegionNow} | {unlockedDate}")
                                        print(
                                            f"[cyan]<{self.config.nickName}>[/cyan]|"
                                            f"[bold blue]BY[/bold blue]| {eventTitle} |"
                                            f"[bold blue]GET[/bold blue]| {dropItem} |"
                                            f"[bold blue]ON[/bold blue]| {dropRegionNow} |"
                                            f"[bold blue] {unlockedDate}")
                                        if self.config.desktopNotify:
                                            desktopNotify(
                                                poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg, dropRegionNow)
                                        if self.config.connectorDropsUrl != "":
                                            self.notifyDrops(
                                                poweredByImg, productImg, eventTitle, unlockedDate, dropItem, dropItemImg, dropRegionNow)
                                    sleep(3)
                                self.isNotified[dropRegionNow] = self.isNotified.get(dropRegionNow, 0) + dropsNeedNotify
                        totalDropsNumber = totalDropsNumber + dropNumberNow
                    self.totalWatchHours = totalWatchHours
                    return totalDropsNumber, dropNumberInfo
                except Exception:
                    print(_("统计掉落失败", color="red"))
                    self.log.error(_log("统计掉落失败"))
                    self.log.error(format_exc())
                    self.totalWatchHours = -1
                    return -1, ""

            # First run
            else:
                try:
                    for i in range(0, len(dropRegion)):
                        if dropNumber[i].text[:-6] == '':
                            continue
                        self.dropsDict[dropRegion[i].text] = int(
                            dropNumber[i].text[:-6])
                        totalDropsNumber = totalDropsNumber + int(dropNumber[i].text[:-6])
                    self.historyDrops = totalDropsNumber
                    self.totalWatchHours = totalWatchHours
                    return totalDropsNumber, ""
                except Exception:
                    print(_("初始化掉落数失败", color="red"))
                    self.log.error(_log("初始化掉落数失败"))
                    self.log.error(format_exc())
                    self.historyDrops = -1
                    self.totalWatchHours = -1
                    return -1, ""
        else:
            self.historyDrops = -1
            self.totalWatchHours = -1
            return -1, ""

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
            rewardWindow = self.driver.current_window_handle
            # Initialize drop count
            if newTab:
                self.countDrops(rewardWindow=rewardWindow, isInit=newTab)
            return rewardWindow
        except Exception:
            print(_("检查掉落数失败", color="red"))
            self.log.error(_log("检查掉落数失败"))
            self.log.error(format_exc())
