import sys
from time import sleep, strftime
from traceback import format_exc

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager
from plyer import notification
from retrying import retry
from rich import print

enUSI18n = {
        "生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开": "WebDriver generation failure!\nThe latest version of Google Chrome is not found.\nPlease check if Chrome downloaded or has the latest version.\nYou can also try to launch the program as an administrator",
        "生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是否打开着谷歌浏览器?请关闭后再次尝试": "WebDriver generation failure!\nIs Google Chrome installed?\nIs Google Chrome currently open? Please close it and try again",
        "生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用": "WebDriver generation failure!\nIs Google Chrome installed?\nIs there a network problem? Check VPN availability if one connected",
        "无法打开Lolesports网页，网络问题，将于3秒后退出...": "Network problem: cannot open LolEsports website. Exiting in 3 seconds...",
        "自动登录失败,检查网络和账号密码": "Automatic login failed. Please check the network availability and account credentials.",
        "好嘞 登录成功": "Logged in successfully.",
        "使用浏览器缓存 自动登录成功": "Using browser cookies. Auto-login success.",
        "观看结束": "Watch finished.",
        "切换语言成功": "Language switched successfully.",
        "切换语言失败": "The language switch failed.",
        "无法登陆，账号密码可能错误或者网络出现问题": "Login failed: wrong credentials or network problem.",
        "开始重试": "Restarting.",
        "配置文件找不到": "Configuration file not found.",
        "按回车键退出": "Press Enter to exit.",
        "配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格,配置路径如有单斜杠请改为双斜杠": "Configuration file format error.\nPlease check if there are Chinese characters and single spaces after colons.\nChange single slash to double in configuration path if there are any.",
        "配置文件中没有账号密码信息": "There are no account credentials in the configuration file.",
        "检查间隔配置错误,已恢复默认值": "Incorrect interval configuration. The default value has been restored.",
        "睡眠时间段配置错误,已恢复默认值": "Incorrect sleep time preiod. The default value has been restored.",
        "最大运行时间配置错误,已恢复默认值": "The maximum runtime set incorrectly. The default value has been restored.",
        "代理配置错误,已恢复默认值": "Incorrect proxy configuration. The default setting has been restored.",
        "用户数据userDataDir路径配置错误,已恢复默认值": "Incorrect UserDataDirectory path configuration. The default setting has been restored.",
        "语言配置错误,已恢复zh_CN默认值": "Incorrect language configuration. The default language zh_CN has been restored.",
        '正常观看 可获取奖励': "is live and being watched. Stream title:",
        "观看异常 重试中...": "is live, but watch attempt was unsuccessful. Retrying...",
        "观看异常": "Watch system work anomaly.",
        "检查掉落失败": "Drops check failed.",
        "掉落提醒失败": "Drop alert failed.",
        "无法打开Lolesports网页，网络问题": "Network error. Cannot open LolEsports website.",
        "登录中...": "Logging in...",
        "账密 提交成功": "Account credentials inserted...",
        "网络问题 登录超时": "Network error. Login timeout.",
        "请输入二级验证代码:": "Please enter 2FA code:",
        "二级验证代码提交成功": "2FA code submitted successfully.",
        "免密登录失败,请去浏览器手动登录后再行尝试": "Authentication failure. Please log in manually using browser and try again.",
        "检查掉落数失败": "Failed to check drop count.",
        "开始检查...": "Start checking...",
        "本次运行掉落总和:": "Session drops: ",
        "生涯总掉落:": "Lifetime drops: ",
        "没有赛区正在直播": "No live broadcasts.",
        "个赛区正在直播中": "match currently live.",
        "赛区正在直播中": "matches currently live.",
        "处于休眠时间，检查时间间隔为1小时": "During the sleep period, the check interval is 1 hour.",
        "下一次检查在:": "Next check at:",
        "预计结束程序时间:": "Time left until the program will auto-close:",
        "对应窗口找不到": "The corresponding window cannot be found.",
        "发生错误": "An error has occurred.",
        "获取比赛列表失败": "Failed to get live broadcasts list.",
        "比赛结束": "Broadcast ended.",
        "关闭已结束的比赛时发生错误": "An error occurred while closing finished broadcast.",
        "比赛跳过": " match skipped.",
        "关闭视频流失败.": "Failed to close stream.",
        "视频流关闭成功.": "Stream closed successfully.",
        "Twitch 160p清晰度设置成功": "Twitch stream quality successfully set to 160p.",
        "Twitch 清晰度设置失败": "Failed to set Twitch stream quality.",
        "无法设置 Twitch 清晰度.": "Unable to set Twitch stream quality.",
        "Youtube 144p清晰度设置成功": "YouTube stream quality successfully set to 144p.",
        "Youtube 清晰度设置失败": "Failed to set YouTube stream quality.",
        "无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者": "Unable to set YouTube stream quality.Stream possibly was misidentified as YouTube source. Please contact the developer.",
        "下一场比赛时间:": "Next broadcast at:",
        "获取下一场比赛时间失败": "Failed to get next broadcast time.",
        "获取掉落数失败": "Failed to get drops count.",
        "本次运行掉落详细:": "Details of this session drops:",
        "统计掉落失败": "Failed to count drops.",
        "初始化掉落数失败": "Failed to initialize drop count.",
        "小傻瓜，出事啦": "Hey, something is wrong.",
        "错误提醒发送成功": "Error alert sent successfully.",
        "错误提醒发送失败": "Failed to send error alert.",
        "异常提醒成功": "Exception error alert successful.",
        "异常提醒失败": "Exception error alert failed.",
        "下载override文件失败": "Failed to import override file.",
        "正在准备中...": "Preparing...",
        "不支持的操作系统": "Unsupported OS.",
        "程序设定运行时长已到，将于60秒后关机,请及时做好准备工作": "The program has reached the set runtime. The system will shut down in 60 seconds. Please prepare accordingly.",
        "关闭所有窗口时发生异常": "An exception occurred while closing all windows.",
        "所有窗口已关闭": "All tabs closed.",
        "处于休眠时间...": "Sleeping...",
        "预计休眠状态将持续到": "The sleep period will last until",
        "点": "o'clock.",
        "通知类型配置错误,已恢复默认值": "Incorrect notification type configuration. The default setting has been restored.",
        "从github获取override文件失败, 将尝试从gitee获取": "Failed to get override file from Github. Trying to get it from Gitee...",
        "获取override文件成功": "Override file successfully imported.",
        "获取override文件失败": "Failed to import override file.",
        "休眠时间结束": "Waking up...",
        "进入休眠时间": "Going to sleep now...",
        "检查下一场比赛时 过滤失效的比赛": "Filtering invalid broadcasts when checking next broadcast.",
        "总观看时长: ": "Overall hours watched: ",
        "日期: ": "Date: ",
        "下次检查在:": "Next check at:",
        "人观看": "viewers",
        "掉落提醒成功": "Drop alert successful.",
        "检查赛区直播状态...": "Checking live broadcasts...",
        "识别到距离比赛时间较长 检查间隔为1小时": "Plenty of time until the next match. Checking interval set to 1 hour.",
        "提醒: 由于已关闭统计掉落功能,webhook提示掉落功能也将关闭": "Tip: The drop count function has been disabled, the drop notification function will also be disabled.",
        "获取LoLEsports网站失败，正在重试...": "Getting to LoLEsports website failed, retrying...",
        }
zhTWI18n = {
    '生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n或可以尝试用管理员方式打开': '生成WEBDRIVER失敗!\n無法找到最新版谷歌瀏覽器!如沒有下載或不是最新版請檢查好再次嘗試\n或可以嘗試用管理員方式開啟',
    '生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是否打开着谷歌浏览器?请关闭后再次尝试': '生成WEBDRIVER失敗!\n是否有谷歌瀏覽器?\n是否開啟著谷歌瀏覽器?請關閉後再次嘗試',
    '生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用': '生成WEBDRIVER失敗!\n是否有谷歌瀏覽器?\n是不是網路問題?請檢查VPN節點是否可用',
    '无法打开Lolesports网页，网络问题，将于3秒后退出...': '無法開啟Lolesports網頁，網路問題，將於3秒後退出...',
    '自动登录失败,检查网络和账号密码': '自動登入失敗,檢查網路和帳號密碼',
    '好嘞 登录成功': '好嘞 登入成功',
    '使用浏览器缓存 自动登录成功': '使用瀏覽器快取 自動登入成功',
    '观看结束': '觀看結束',
    '切换语言成功': '切換語言成功',
    '切换语言失败': '切換語言失敗',
    '无法登陆，账号密码可能错误或者网络出现问题': '無法登陸，帳號密碼可能錯誤或者網路出現問題',
    '开始重试': '開始重試',
    '配置文件找不到': '配置檔案找不到',
    '按回车键退出': '按回車鍵退出',
    '配置文件格式错误,请检查是否存在中文字符以及冒号后面应该有一个空格,配置路径如有单斜杠请改为双斜杠': '配置檔案格式錯誤,請檢查是否存在中文字元以及冒號後面應該有一個空格,配置路徑如有單斜槓請改為雙斜槓',
    '配置文件中没有账号密码信息': '配置檔案中沒有帳號密碼資訊',
    '检查间隔配置错误,已恢复默认值': '檢查間隔配置錯誤,已恢復預設值',
    '睡眠时间段配置错误,已恢复默认值': '睡眠時間段配置錯誤,已恢復預設值',
    '最大运行时间配置错误,已恢复默认值': '最大執行時間配置錯誤,已恢復預設值',
    '代理配置错误,已恢复默认值': '代理配置錯誤,已恢復預設值',
    '用户数据userDataDir路径配置错误,已恢复默认值': '使用者資料userDataDir路徑配置錯誤,已恢復預設值',
    '语言配置错误,已恢复zh_CN默认值': '語言配置錯誤,已恢復zh_CN預設值',
    '正常观看 可获取奖励': '正常觀看 可獲取獎勵',
    '观看异常 重试中...': '觀看異常 重試中...',
    '观看异常': '觀看異常',
    '检查掉落失败': '檢查掉落失敗',
    '掉落提醒失败': '掉落提醒失敗',
    '无法打开Lolesports网页，网络问题': '無法開啟Lolesports網頁，網路問題',
    '登录中...': '登入中...',
    '账密 提交成功': '帳密 提交成功',
    '网络问题 登录超时': '網路問題 登入超時',
    '请输入二级验证代码:': '請輸入二級驗證程式碼:',
    '二级验证代码提交成功': '二級驗證程式碼提交成功',
    '免密登录失败,请去浏览器手动登录后再行尝试': '免密登入失敗,請去瀏覽器手動登入後再行嘗試',
    '检查掉落数失败': '檢查掉落數失敗',
    '开始检查...': '開始檢查...',
    '本次运行掉落总和:': '本次執行掉落總和:',
    '生涯总掉落:': '生涯總掉落:',
    '没有赛区正在直播': '沒有賽區正在直播',
    '个赛区正在直播中': '個賽區正在直播中',
    '赛区正在直播中': '賽區正在直播中',
    '处于休眠时间，检查时间间隔为1小时': '處於休眠時間，檢查時間間隔為1小時',
    '下一次检查在:': '下一次檢查在:',
    '预计结束程序时间:': '預計結束程式時間:',
    '对应窗口找不到': '對應視窗找不到',
    '发生错误': '發生錯誤',
    '获取比赛列表失败': '獲取比賽列表失敗',
    '比赛结束': '比賽結束',
    '关闭已结束的比赛时发生错误': '關閉已結束的比賽時發生錯誤',
    '比赛跳过': '比賽跳過',
    '关闭视频流失败.': '關閉影片流失敗.',
    '视频流关闭成功.': '影片流關閉成功.',
    'Twitch 160p清晰度设置成功': 'Twitch 160p清晰度設定成功',
    'Twitch 清晰度设置失败': 'Twitch 清晰度設定失敗',
    '无法设置 Twitch 清晰度.': '無法設定 Twitch 清晰度.',
    'Youtube 144p清晰度设置成功': 'Youtube 144p清晰度設定成功',
    'Youtube 清晰度设置失败': 'Youtube 清晰度設定失敗',
    '无法设置 Youtube 清晰度.可能是误判成youtube源,请联系作者': '無法設定 Youtube 清晰度.可能是誤判成youtube源,請聯絡作者',
    '下一场比赛时间:': '下一場比賽時間:',
    '获取下一场比赛时间失败': '獲取下一場比賽時間失敗',
    '获取掉落数失败': '獲取掉落數失敗',
    '本次运行掉落详细:': '本次執行掉落詳細:',
    '统计掉落失败': '統計掉落失敗',
    '初始化掉落数失败': '初始化掉落數失敗',
    '小傻瓜，出事啦': '小傻瓜，出事啦',
    '错误提醒发送成功': '錯誤提醒傳送成功',
    '错误提醒发送失败': '錯誤提醒傳送失敗',
    '异常提醒成功': '異常提醒成功',
    '异常提醒失败': '異常提醒失敗',
    '下载override文件失败': '下載override檔案失敗',
    '正在准备中...': '正在準備中...',
    '不支持的操作系统': '不支援的作業系統',
    '程序设定运行时长已到，将于60秒后关机,请及时做好准备工作': '程式設定執行時長已到，將於60秒後關機,請及時做好準備工作',
    '关闭所有窗口时发生异常': '關閉所有視窗時發生異常',
    '所有窗口已关闭': '所有視窗已關閉',
    '处于休眠时间...': '處於休眠時間...',
    '预计休眠状态将持续到': '預計休眠狀態將持續到',
    '点': '點',
    '通知类型配置错误,已恢复默认值': '通知型別配置錯誤,已恢復預設值',
    '从github获取override文件失败, 将尝试从gitee获取': '從github獲取override檔案失敗, 將嘗試從gitee獲取',
    '获取override文件成功': '獲取override檔案成功',
    '获取override文件失败': '獲取override檔案失敗',
    '休眠时间结束': '休眠時間結束',
    '进入休眠时间': '進入休眠時間',
    '检查下一场比赛时 过滤失效的比赛': '檢查下一場比賽時 過濾失效的比賽',
    '总观看时长: ': '總觀看時長: ',
    '日期: ': '日期: ',
    '下次检查在:': '下次檢查在:',
    '人观看': '人觀看',
    '掉落提醒成功': '掉落提醒成功',
    '检查赛区直播状态...': '檢查賽區直播狀態...',
    '识别到距离比赛时间较长 检查间隔为1小时': '識別到距離比賽時間較長 檢查間隔為1小時',
    '提醒: 由于已关闭统计掉落功能,webhook提示掉落功能也将关闭': '提醒: 由於已關閉統計掉落功能,webhook提示掉落功能也將關閉',
    "获取LoLEsports网站失败，正在重试...": "獲取LoLEsports網站失敗，正在重試...",
}


def _(text, color, lang="zh_CN"):
    """
    A function that formats text with a specified color based on the given language.

    Args:
        text (str): The text to be formatted.
        color (str): The color to format the text with, specified using BBCode format.
        lang (str): The language of the text. Defaults to "zh_CN".

    Returns:
        str: The formatted text with the specified color and language.
    """
    rawText = text
    language_map = {
        "zh_CN": f"[{color}]{text}[/{color}]",
        "en_US": f"[{color}]{enUSI18n.get(text, f'{rawText} No translation there. Please contact the developer.')}[/{color}]",
        "zh_TW": f"[{color}]{zhTWI18n.get(text, rawText)}[/{color}]"
    }
    return language_map.get(lang, text)


def _log(text, lang="zh_CN"):
    """
    Logs the given text with language support.

    Args:
        text (str): The text to be logged.
        lang (str, optional): The language of the text. Defaults to "zh_CN".

    Returns:
        str: The logged text in the specified language, or the original text if translation is not available.
    """
    rawText = text
    language_map = {
        "zh_CN": text,
        "en_US": enUSI18n.get(text, f"{rawText} No translation there. Please contact the developer."),
        "zh_TW": zhTWI18n.get(text, rawText)
    }
    return language_map.get(lang, text)


class Utils:
    def __init__(self, config):
        self.config = config
        pass

    def errorNotify(self, error):
        """
        Sends error notifications to selected channels based on the user's configuration settings.

        Args:
            error (str): The error message to be included in the notification.

        """
        notifyType = self.config.notifyType
        needDesktopNotify = self.config.desktopNotify
        connectorUrl = self.config.connectorDropsUrl
        language = self.config.language
        if notifyType in ["all", "error"]:
            if needDesktopNotify:
                try:
                    notification.notify(
                        title=_log("小傻瓜，出事啦", lang=language),
                        message=f"Error Message: {error}",
                        timeout=30
                    )
                    print(_("错误提醒发送成功", color="green", lang=language))
                    log.info(_log("错误提醒发送成功", lang=language))
                except Exception as e:
                    print(_("错误提醒发送失败", color="red", lang=language))
                    log.error(_log("错误提醒发送失败", lang=language))
                    log.error(format_exc())

            if connectorUrl != "":
                s = requests.session()
                s.keep_alive = False  # 关闭多余连接
                try:
                    if "https://oapi.dingtalk.com" in connectorUrl:
                        data = {
                            "msgtype": "link",
                            "link": {
                                "text": "Alert: Drop farming stopped",
                                "title": error,
                                "picUrl": "",
                                "messageUrl": ""
                            }
                        }
                        s.post(connectorUrl, json=data)

                    elif "https://discord.com/api/webhooks" in connectorUrl:
                        embed = {
                            "title": "Alert: Drop farming stopped",
                            "description": f"{error}",
                            "image": {"url": f""},
                            "thumbnail": {"url": f""},
                            "color": 6676471,
                        }
                        params = {
                            "username": "EsportsHelper",
                            "embeds": [embed]
                        }
                        s.post(connectorUrl, headers={
                            "Content-type": "application/json"}, json=params)

                    else:
                        params = {
                            "text": f"发生错误停止获取Drop{error}",
                        }
                        s.post(connectorUrl, headers={
                            "Content-type": "application/json"}, json=params)

                    log.info(_log("异常提醒成功", lang=language))
                    print(_("异常提醒成功", color="green", lang=language))
                except Exception as e:
                    print(_("异常提醒失败", color="red", lang=language))
                    log.error(_log("异常提醒失败", lang=language))
                    log.error(format_exc())

    def debugScreen(self, driver, lint=""):
        """
        Function Name: debugScreen
        Input:
            - driver: webdriver object
            - lint: string (default: "")
        Output: None
        Purpose: Saves a screenshot of the current webpage for debugging purposes.
                 The screenshot is saved to ./logs/pics/ directory with a timestamp and a lint identifier.
                 If the lint parameter is not specified, an empty string will be used as the identifier.
        """
        try:
            if self.config.debug:
                log.info(f"DebugScreen: {lint} Successful")
                driver.save_screenshot(
                    f"./logs/pics/{strftime('%b-%d-%H-%M-%S')}-{lint}.png")
        except Exception:
            log.error("DebugScreen: Failed")
            log.error(format_exc())

    def info(self):
        version = VersionManager.getVersion()
        githubUrl = "https://github.com/Yudaotor/EsportsHelper"
        VersionManager.checkVersion()
        if self.config.language == "zh_CN":
            print(
                f"[bold yellow]>_<"
                f"{'=' * 27}"
                f">_<"
                f"{'=' * 27}"
                f">_<[/bold yellow]"
            )
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]        "
                  f"感谢使用 [cyan]电竞助手[/cyan] v{version}!        "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 12}[/bold yellow] "
                  f"本程序开源于github链接地址如下: "
                  f"[bold yellow]{'=' * 12}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]   "
                  f"{githubUrl}     "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"如觉得不错的话可以进上面链接请我喝杯咖啡支持下. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"请在使用前[red]阅读教程文件[/red], 以确保你的配置符合要求! "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]  "
                  f"如需关闭请勿直接右上角X关闭，请按Ctrl+C来关闭. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(
                f"[bold yellow]>_<"
                f"{'=' * 27}"
                f">_<"
                f"{'=' * 27}"
                f">_<[/bold yellow]"
            )
            print()
        elif self.config.language == "en_US":
            print(
                f"[bold yellow]>_<"
                f"{'=' * 27}"
                f">_<"
                f"{'=' * 27}"
                f">_<[/bold yellow]"
            )
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow] "
                  f"Thanks for using [cyan]EsportsHelper[/cyan] v{version}!  "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]   "
                  f"The program is open source at GitHub  "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]    "
                  f"{githubUrl}    [bold yellow]{'=' * 4}"
                  f">_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]      "
                  f"If you like it, please give me a star      "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(
                f"[bold yellow]>_<"
                f"{'=' * 27}"
                f">_<"
                f"{'=' * 27}"
                f">_<[/bold yellow]"
            )
            print()
        elif self.config.language == "zh_TW":
            print(
                f"[bold yellow]>_<"
                f"{'=' * 27}"
                f">_<"
                f"{'=' * 27}"
                f">_<[/bold yellow]"
            )
            print(f"[bold yellow]>_<{'=' * 8}[/bold yellow]        "
                  f"感謝使用 [cyan]電競助手[/cyan] v{version}!        "
                  f"[bold yellow]{'=' * 8}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 12}[/bold yellow] "
                  f"本程式開源於github連結地址如下: "
                  f"[bold yellow]{'=' * 12}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]   "
                  f"{githubUrl}     "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"如覺得不錯的話可以進上面連結請我喝杯咖啡支援下. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow] "
                  f"請在使用前[red]閱讀教程檔案[/red], 以確保你的配置符合要求! "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(f"[bold yellow]>_<{'=' * 4}[/bold yellow]  "
                  f"如需關閉請勿直接右上角X關閉，請按Ctrl+C來關閉. "
                  f"[bold yellow]{'=' * 4}>_<[/bold yellow]")
            print(
                f"[bold yellow]>_<"
                f"{'=' * 27}"
                f">_<"
                f"{'=' * 27}"
                f">_<[/bold yellow]"
            )
            print()

    def getOverrideFile(self):
        """
        Function Name: getOverrideFile
        Output: Dictionary containing overrides from a remote file
        Purpose: Retrieve overrides from a remote file and return them as a dictionary
        """
        try:
            OVERRIDES = {}
            req = requests.session()
            headers = {'Content-Type': 'text/plain; charset=utf-8',
                       'Connection': 'close'}
            try:
                remoteOverrideFile = req.get(
                    "https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt", headers=headers)
            except Exception:
                log.error(_log("从github获取override文件失败, 将尝试从gitee获取", lang=self.config.language))
                print(_("从github获取override文件失败, 将尝试从gitee获取", color="red", lang=self.config.language))
                remoteOverrideFile = req.get(
                    "https://gitee.com/yudaotor/EsportsHelper/raw/main/override.txt", headers=headers)
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
                log.info(_log("获取override文件成功", lang=self.config.language))
                print(_("获取override文件成功", color="green", lang=self.config.language))
                return OVERRIDES
            else:
                print(_("获取override文件失败", color="red", lang=self.config.language))
                log.error(_log("获取override文件失败", lang=self.config.language))
                input(_log("按回车键退出", lang=self.config.language))
                sysQuit(e=_log("获取override文件失败", lang=self.config.language))
        except Exception:
            log.error(_log("获取override文件失败", lang=self.config.language))
            print(_("获取override文件失败", color="red", lang=self.config.language))
            input(_log("按回车键退出", lang=self.config.language))
            sysQuit(e=_log("获取override文件失败", lang=self.config.language))


def desktopNotify(poweredByImg, productImg, unlockedDate, eventTitle, dropItem, dropItemImg, dropLocale):
    """
    Desktop notification function that sends a notification to the user's desktop.

    Args:
    poweredByImg (str): The image URL of the company that powers the event.
    productImg (str): The image URL of the product being dropped.
    unlockedDate (str): The date and time when the drop will be unlocked.
    eventTitle (str): The title of the event.
    dropItem (str): The name of the dropped item.
    dropItemImg (str): The image URL of the dropped item.
    dropLocale (str): The location where the drop will occur.

    """
    try:
        notification.notify(
            title="New drop!",
            message=f"BY {eventTitle} GET{dropItem} ON{dropLocale} {unlockedDate}",
            timeout=30
        )
        log.info("Desktop notification sent successfully")
    except Exception:
        log.error("Desktop notification failed")
        log.error(format_exc())


def sysQuit(driver=None, e=None):
    """
    Function: sysQuit
    Description: Safely quits the webdriver and exits the program.
    Input:
        - driver: Webdriver instance to be quit
        - e: Exception that occurred (optional)
    Output: None
    """
    sleep(3)
    if driver:
        driver.quit()
    log.error(e)
    log.info("------Quit------")
    sys.exit()


def getMatchName(url: str) -> str:
    """
    Returns the name of the match corresponding to the given URL.

    Args:
        url (str): A string that represents a URL.

    Returns:
        str: A string that represents the name of the match.
    """
    match = url.split('/')[-2] if url.split('/')[-2] != "live" else url.split('/')[-1]
    match = "cblol" if match == "cblol-brazil" else match
    match = "ljl" if match == "ljl-japan" else match
    match = "tft_rising_legends" if match == "tft_esports" else match
    return match


# Repeat the attempt to fetch the page up to 4 times,
# and the wait time is based on 2 minutes, each time incremented by 2 minutes
@retry(stop_max_attempt_number=4, wait_incrementing_increment=120000, wait_incrementing_start=120000)
def getLolesportsWeb(driver, language):
    """
    Retrieves the Lolesports website using the provided driver. If an exception occurs while accessing the website,
    it retries for a maximum of four times, incrementing the wait time between each attempt by two minutes.

    Args:
    - driver (selenium.webdriver.remote.webdriver.WebDriver): The driver to use for accessing the Lolesports website
    - language (str): The language to use for log
    """
    try:
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,"
            "lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,"
            "lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,"
            "emea_masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,"
            "superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,"
            "arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,"
            "liga_master_flo,movistar_fiber_golden_league,elements_league,"
            "claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,"
            "msi,tft_esports"
        )
        # Whether the load is complete
        wait = WebDriverWait(driver, 20)
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "div.results-label")))

    except Exception:
        print(_("获取LoLEsports网站失败，正在重试...", color="red", lang=language))
        log.error(_log("获取LoLEsports网站失败，正在重试...", lang=language))
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,"
            "lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,"
            "lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,"
            "emea_masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,"
            "superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,"
            "arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,"
            "liga_master_flo,movistar_fiber_golden_league,elements_league,"
            "claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,"
            "msi,tft_esports"
        )
        # Whether the load is complete
        wait = WebDriverWait(driver, 20)
        wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "div.results-label")))



