import sys
from time import sleep, strftime
from traceback import format_exc, print_exc

import requests
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager
from plyer import notification
from retrying import retry
from rich import print
from urllib3.exceptions import MaxRetryError

i18n = {"눈_눈 生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开\n按任意键退出...": "WebDriver generation failure!\nThe latest version of Google Chrome is not found.\nPlease check if Chrome downloaded or has the latest version.\nYou can also try to launch the program as an administrator.\nExit the program by pressing any key...",
        "눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是否打开着谷歌浏览器?请关闭后再次尝试\n按任意键退出...": "WebDriver generation failure!\nIs Google Chrome installed?\nIs Google Chrome currently open? Please close it and try again.\nExit the program by pressing any key...",
        "눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用\n按任意键退出...": "WebDriver generation failure!\nIs Google Chrome installed?\nIs there a network problem? Check VPN availability if one connected.\nExit the program by pressing any key...",
        "Π——Π 无法打开Lolesports网页，网络问题，将于3秒后退出...": "Network problem: cannot open LolEsports website. Exiting in 3 seconds...",
        "눈_눈 自动登录失败,检查网络和账号密码": "Automatic login failed. Please check the network availability and account credentials.",
        "∩_∩ 好嘞 登录成功": "Logged in successfully.",
        "∩_∩ 使用系统数据 自动登录成功": "Using browser cookies. Auto-login success.",
        "观看结束～": "Watch finished.",
        "切换语言成功": "Language switched successfully.",
        "切换语言失败": "The language switch failed.",
        "无法登陆，账号密码可能错误或者网络出现问题": "Login failed: wrong credentials or network problem.",
        "눈_눈 开始重试": "Restarting.",
        "配置文件找不到": "Configuration file not found.",
        "按任意键退出": "Exit the program by pressing any key.",
        "配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格,配置路径如有单斜杠请改为双斜杠": "Configuration file format error.\nPlease check if there are Chinese characters and single spaces after colons.\nChange single slash to double in configuration path if there are any.",
        "配置文件中没有账号密码信息": "There are no account credentials in the configuration file.",
        "检查间隔配置错误,已恢复默认值": "Incorrect interval configuration. The default value has been restored.",
        "睡眠时间段配置错误,已恢复默认值": "Incorrect sleep time preiod. The default value has been restored.",
        "最大运行时间配置错误,已恢复默认值": "The maximum runtime set incorrectly. The default value has been restored.",
        "代理配置错误,已恢复默认值": "Incorrect proxy configuration. The default setting has been restored.",
        "用户数据userDataDir路径配置错误,已恢复默认值": "Incorrect UserDataDirectory path configuration. The default setting has been restored.",
        "语言配置错误,已恢复zh_CN默认值": "Incorrect language configuration. The default language zh_CN has been restored.",
        '正常观看 可获取奖励': "Watch system operational. Drops available.",
        "观看异常 重试中...": "Watch system work anomaly. Retrying...",
        "观看异常": "Watch system work anomaly.",
        "〒.〒 检查掉落失败": "Drops check failed.",
        "〒.〒 掉落提醒失败": "Drop alert failed.",
        "Π——Π 无法打开Lolesports网页，网络问题": "Network error. Cannot open LolEsports website.",
        "눈_눈 登录中...": "Logging in...",
        "∩_∩ 账密 提交成功": "Account credentials sent successfully.",
        "×_× 网络问题 登录超时": "Network error. Login timeout.",
        "请输入二级验证代码:": "Please enter 2FA code:",
        "二级验证代码提交成功": "2FA code submitted successfully.",
        "免密登录失败,请去浏览器手动登录后再行尝试": "Authentication failure. Please log in manually using browser and try again.",
        "检查掉落数失败": "Failed to check drop count.",
        "●_● 开始检查...": "Checking...",
        "$_$ 本次运行掉落总和:": "Session drops:",
        "生涯总掉落:": "Lifetime drops:",
        "〒.〒 没有赛区正在直播": "No live broadcasts.",
        "赛区正在直播中": "The match is currently live.",
        "处于休眠时间，检查时间间隔为1小时": "During the sleep period, the check interval is 1 hour.",
        "下一次检查在:": "Next check in:",
        "预计结束程序时间:": "Time left until the program will auto-close:",
        "Q_Q 对应窗口找不到": "The corresponding window cannot be found.",
        "Q_Q 发生错误": "An error has occurred.",
        "Q_Q 获取比赛列表失败": "Failed to get live broadcasts list.",
        "比赛结束": "Broadcast ended.",
        "Q_Q 关闭已结束的比赛时发生错误": "An error occurred while closing finished broadcast.",
        "比赛跳过": " match skipped.",
        "°D° 关闭 Twitch 流失败.": "Failed to close Twitch stream.",
        ">_< Twitch 160p清晰度设置成功": "Twitch stream resolution successfully set to 160p.",
        ">_< Twitch 流关闭成功": "Twitch stream closed successfully.",
        "°D° Twitch 清晰度设置失败": "Failed to set Twitch stream resolution.",
        "°D° 无法设置 Twitch 清晰度.": "Unable to set Twitch stream resolution.",
        "°D° 关闭 Youtube 流失败.": "Failed to close YouTube stream.",
        ">_< Youtube 流关闭成功": "YouTube stream closed successfully.",
        ">_< Youtube 144p清晰度设置成功": "YouTube stream resolution successfully set to 144p.",
        "°D° Youtube 清晰度设置失败": "Failed to set YouTube stream resolution.",
        "°D° 无法设置 Youtube 清晰度.": "Unable to set YouTube stream resolution.",
        "下一场比赛时间:": "Time of the next broadcast:",
        "Q_Q 获取下一场比赛时间失败": "Failed to get next broadcast time.",
        "Q_Q 获取掉落数失败": "Failed to get drops count.",
        "$_$ 本次运行掉落详细:": "Details of this session drops:",
        "QAQ 统计掉落失败": "Failed to count drops.",
        "QAQ 初始化掉落数失败": "Failed to initialize drop count.",
        "小傻瓜，出事啦": "Hey, something is wrong.",
        "错误提醒发送成功": "Error alert sent successfully.",
        "错误提醒发送失败": "Failed to send error alert.",
        ">_< 异常提醒成功": "Exception error alert successful.",
        "异常提醒失败": "Exception error alert failed.",
        "下载override文件失败": "Failed to import override file.",
        "ㅍ_ㅍ 正在准备中...": "Preparing...",
        "不支持的操作系统": "Unsupported OS.",
        "程序设定运行时长已到，将于60秒后关机,请及时做好准备工作": "The program has reached the set runtime. The system will shut down in 60 seconds. Please prepare accordingly.",
        "Q_Q 关闭所有窗口时发生异常": "An exception occurred while closing all windows.",
        "Q_Q 所有窗口已关闭": "All windows closed.",
        "处于休眠时间...": "Sleeping...",
        "预计休眠状态将持续到": "The sleep period will last until",
        "点": "o'clock.",
        }


class Utils:
    def __init__(self, config):
        self.config = config
        pass

    def errorNotify(self, error):
        error = ""
        if self.config.desktopNotify:
            try:
                notification.notify(
                    title=_log("小傻瓜，出事啦", lang=self.config.language),
                    message=f"Error Message: {error}",
                    timeout=30
                )
                print(_("错误提醒发送成功", color="green", lang=self.config.language))
                log.info(_log("错误提醒发送成功", lang=self.config.language))
            except Exception as e:
                print(_("错误提醒发送失败", color="red", lang=self.config.language))
                log.error(_log("错误提醒发送失败", lang=self.config.language))
                log.error(format_exc())
        if self.config.connectorDropsUrl != "":
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            try:
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Stop Farming Drop",
                            "title": error,
                            "picUrl": "",
                            "messageUrl": ""
                        }
                    }
                    s.post(self.config.connectorDropsUrl, json=data)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    embed = {
                        "title": "Stop Farming Drop",
                        "description": f"{error}",
                        "image": {"url": f""},
                        "thumbnail": {"url": f""},
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"发生错误停止获取Drop{error}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                else:
                    params = {
                        "text": f"发生错误停止获取Drop{error}",
                    }
                    s.post(self.config.connectorDropsUrl, headers={
                           "Content-type": "application/json"}, json=params)
                log.info(_log(">_< 异常提醒成功", lang=self.config.language))
                print(_("异常提醒成功", color="green", lang=self.config.language))
            except Exception as e:
                print(_("异常提醒失败", color="red", lang=self.config.language))
                log.error(_("异常提醒失败", lang=self.config.language))
                log.error(format_exc())

    def debugScreen(self, driver, lint=""):
        try:
            if self.config.debug:
                log.info(f"DebugScreen: {lint} Successful")
                driver.save_screenshot(
                    f"./logs/pics/{strftime('%b-%d-%H-%M-%S')}-{lint}.png")
        except Exception:
            log.error("DebugScreen: Failed")
            log.error(format_exc())

    def info(self):
        if self.config.language == "zh_CN":
            print("[green]=========================================================")
            print(
                f"[green]========[/green]        感谢使用 [blue]电竞助手[/blue] v{VersionManager.getVersion()}!        [green]========[/green]")
            print(
                "[green]============[/green] 本程序开源于github链接地址如下: [green]============[/green]")
            print(
                "[green]====[/green]   https://github.com/Yudaotor/EsportsHelper     [green]====[/green]")
            print("[green]====[/green] 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. [green]====[/green]")
            print(
                "[green]====[/green] 请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! [green]====[/green]")
            print(
                "[green]====[/green]  如需关闭请勿直接右上角X关闭，请按Ctrl+C来关闭. [green]====[/green]")
            print("[green]=========================================================")
            print()
            VersionManager.checkVersion()
        elif self.config.language == "en_US":
            print("[green]=========================================================")
            print(
                f"[green]========[/green] Thanks for using [blue]EsportsHelper[/blue] v{VersionManager.getVersion()}!  [green]========[/green]")
            print(
                "[green]=========[/green]  The program is open source at github  [green]=========[/green]")
            print(
                "[green]====[/green]    https://github.com/Yudaotor/EsportsHelper[green]    ====[/green]")
            print(
                "[green]====[/green]      If you like it, please give me a star      [green]====[/green]")
            print("[green]=========================================================")


def desktopNotify(poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg):
    try:
        notification.notify(
            title="Get Drop!",
            message=f"BY {eventTitle} GET{dropItem} {unlockedDate}",
            timeout=30
        )
        log.info("Desktop Notify Successful")
    except Exception as e:
        log.error("Desktop Notify Failed")
        log.error(format_exc())


def sysQuit(driver=None, e=None):
    sleep(3)
    if driver:
        driver.quit()
    log.error(e)
    log.info("------Quit------")
    sys.exit()


def downloadOverrideFile():
    try:
        OVERRIDES = {}
        req = requests.session()
        headers = {'Content-Type': 'text/plain; charset=utf-8',
                   'Connection': 'close'}
        remoteOverrideFile = req.get(
            "https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt", headers=headers)
        if remoteOverrideFile.status_code == 200:
            override = remoteOverrideFile.text.split(",")
            first = True
            for o in override:
                temp = o.split("|")
                if len(temp) == 2:
                    if first:
                        first = False
                    else:
                        temp[0] = temp[0][1:]
                    OVERRIDES[temp[0]] = temp[1]
            return OVERRIDES
        else:
            log.error("get overrides file failed")
            input("Press any key to exit...")
            sys.exit()
    except MaxRetryError:
        log.error("get overrides file failed")
        print(f"[red]get overrides file failed, Try later[/red]")
        input("Press any key to exit...")
        sysQuit(e="get overrides file failed")
    except Exception as ex:
        print_exc()
        log.error("get overrides file failed")
        print(f"[red]get overrides file failed, Try later[/red]")
        input("Press any key to exit...")
        sysQuit(e="get overrides file failed")


# 从url中获取比赛赛区名
def getMatchName(url) -> str:
    splitUrl = url.split('/')
    if splitUrl[-2] != "live":
        match = splitUrl[-2]
    else:
        match = splitUrl[-1]
    if "cblol-brazil" == match:
        match = "cblol"
    elif "ljl-japan" == match:
        match = "ljl"
    return match


# 重复尝试获取网页最多4次，等待时间以2分钟为基数，每次递增2分钟
@retry(stop_max_attempt_number=4, wait_incrementing_increment=120000, wait_incrementing_start=120000)
def getLolesportsWeb(driver):
    try:
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,emea_masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
    except Exception:
        print("[red]Get LoLesports Web Page Failed,Retrying...[/red]")
        log.error("Get LoLesports Web Page Failed,Retrying...")
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,emea_masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")


def _(text, color, lang="zh_CN"):
    if lang == "zh_CN":
        return f"[{color}]{text}"
    elif lang == "en_US":
        return f"[{color}]{i18n.get(text)}"


def _log(text, lang="zh_CN"):
    if lang == "zh_CN":
        return f"{text}"
    elif lang == "en_US":
        return f"{i18n.get(text)}"
