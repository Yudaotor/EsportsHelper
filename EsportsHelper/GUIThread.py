from threading import Thread
from time import sleep
from traceback import format_exc

from rich.live import Live
from rich.spinner import Spinner
from rich.style import Style
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich import print
from rich.layout import Layout
from EsportsHelper.Config import config
from EsportsHelper.Logger import log
from EsportsHelper.I18n import i18n
from EsportsHelper.Stats import stats
from EsportsHelper.Utils import colorFlicker, getWebhookInfo, \
    getConfigInfo, getLiveRegionsInfo, getNextMatchTimeInfo, \
    getDropInfo, getSleepBalloonsInfo, cleanBriefInfo, \
    getLiveInfo, getInfo, getWarningInfo, formatExc, getSleepPeriodInfo

_ = i18n.getText
_log = i18n.getLog


class GUIThread(Thread):

    def __init__(self, locks):
        super().__init__()
        self.locks = locks

    def setAccountTable(self, frameCount):
        table = Table(expand=True)
        table.style = Style(color="yellow", bold=True)
        spinnerDots = Spinner("dots")
        status = _("状态", color="bold yellow")
        statusPhrases = [_log("检查中"), _log("登录中"), _log("初始化")]
        if any(phrase in stats.status for phrase in statusPhrases):
            status = _("状态", color="bold yellow") + spinnerDots.frames[frameCount % len(spinnerDots.frames)]
        table.add_column(_("昵称", color="bold yellow"), justify="center")
        table.add_column(status, justify="center")
        table.add_column(_("直播赛区", color="bold yellow"), justify="center")
        table.add_column(_("总掉落", color="bold yellow"), justify="center")
        table.add_column(_("总时长", color="bold yellow"), justify="center")
        table.add_column(_("上次检测", color="bold yellow"), justify="center")
        table.add_column(_("下次检测", color="bold yellow"), justify="center")
        table.add_column(_("下场比赛", color="bold yellow"), justify="center")

        liveRegions = getLiveRegionsInfo()
        nextMatchTime = getNextMatchTimeInfo()
        if stats.sessionDrops > 0:
            dropNumber = str(stats.historyDrops) + "+" + str(stats.sessionDrops)
        else:
            dropNumber = str(stats.historyDrops)
        if int(stats.sessionWatchHours) > 0:
            watchHours = str(stats.totalWatchHours) + "+" + str(stats.sessionWatchHours)
        else:
            watchHours = str(stats.totalWatchHours)
        table.add_row(
            f"[bold cyan]{str(config.nickName)}[/bold cyan]",
            str(stats.status),
            str(liveRegions),
            f"[cyan]{dropNumber}[/cyan]",
            f"[cyan]{watchHours}[/cyan]",
            str(stats.lastCheckTime),
            str(stats.nextCheckTime),
            str(nextMatchTime)
        )
        return table

    def run(self):
        try:
            console = Console(force_terminal=True)
            layout = Layout()
            layout.split_column(
                Layout(name="upper"),
                Layout(name="lower")
            )
            layout["upper"].split(
                Layout(name="banner"),
                Layout(name="table", renderable=self.setAccountTable(0))
            )

            is_dockerized = config.isDockerized
            dropInfo = getDropInfo()
            configInfo = getConfigInfo()
            webhookInfo = getWebhookInfo()
            sleepPeriodInfo = getSleepPeriodInfo()
            layout["upper"]["banner"].split_row(
                Layout(name="time", renderable=Panel(" ".join(stats.banner),
                                                     style="bold yellow", title_align="left",
                                                     title=_('电竞助手', color="bold blue") + str(config.version) + " " + sleepPeriodInfo,
                                                     subtitle_align="right", subtitle=configInfo)),
                Layout(name="drop", renderable=Panel(dropInfo,
                                                     title=_('掉宝', color="bold yellow") + f"({_('今日', color='bold yellow')})" + f"-->{stats.sessionDrops}({stats.todayDrops})",
                                                     title_align="left", style="bold yellow", subtitle=webhookInfo, subtitle_align="right"))
            )

            info1, info2 = getInfo()
            width = (console.width - 8) // 2
            liveInfo1, liveInfo2 = getLiveInfo(width)
            cleanBriefInfo()
            modeInfo = ""
            if config.mode == "safe":
                modeInfo = _("安全模式: ", "bold yellow") + "ON"

            layout["lower"].split_column(
                Layout(name="info"),
                Layout(name="live")
            )
            layout["lower"]["live"].split_row(
                Layout(name="live1", renderable=Panel("\n".join(liveInfo1), title=_("直播信息", "bold yellow"), title_align="left", style="bold yellow")),
                Layout(name="live2", renderable=Panel("\n".join(liveInfo2), style="bold yellow", title_align="left", title=modeInfo,
                                                      subtitle=_("请我喝一杯咖啡", "bold cyan") + ":https://github.com/Yudaotor", subtitle_align="right"))
            )
            layout["lower"]["info"].split_row(
                Layout(name="info1", renderable=Panel("\n".join(info1), title=_("简略日志", "bold yellow"), title_align="left", style="bold yellow")),
                Layout(name="info2", renderable=Panel("\n".join(info2), subtitle=_("(详细请见log文件)", "bold yellow"), subtitle_align="right", style="bold yellow"))
            )

            layout["upper"].ratio = 1
            layout["lower"].ratio = 2
            layout["upper"]["banner"].ratio = 1
            layout["upper"]["table"].ratio = 2
            layout["lower"]["live"].ratio = 2
            layout["lower"]["info"].ratio = 3
            frameCount = 0
            with Live(layout, auto_refresh=False, console=console) as live:
                while True:
                    drops = ""
                    if stats.sessionDropsDict:
                        for key in stats.sessionDropsDict:
                            drops += f"{key}: {stats.sessionDropsDict.get(key)}\t"
                    dropInfo = drops if drops else _("暂无掉落", "bold yellow")
                    webhookInfo = getWebhookInfo()
                    layout["upper"]["banner"]["drop"].update(Panel(dropInfo,
                                                                   title=_('掉宝',
                                                                           color="bold yellow") + f"({_('今日', color='bold yellow')})" + f"-->{stats.sessionDrops}({stats.todayDrops})",
                                                                   title_align="left", style="bold yellow", subtitle=webhookInfo, subtitle_align="right"))
                    layout["upper"]["table"].update(self.setAccountTable(frameCount))

                    cleanBriefInfo()
                    width = (console.width - 8) // 2
                    liveInfo1, liveInfo2 = getLiveInfo(width)
                    info1, info2 = getInfo()
                    # color change
                    colorFlicker()
                    frameCount += 1
                    frameCount %= 100
                    warningInfo, liveNumber = getWarningInfo()
                    sleepInfo = getSleepBalloonsInfo(frameCount)
                    sleepPeriodInfo = getSleepPeriodInfo()
                    if config.mode == "safe":
                        modeInfo = _("安全模式: ", "bold yellow") + "ON"
                    watchRegion = stats.watchRegion
                    layout["upper"]["banner"]["time"].update(Panel(" ".join(stats.banner),
                                                                   style="bold yellow", title_align="left",
                                                                   title=_('电竞助手', color="bold blue") + str(config.version) + " " + sleepPeriodInfo + " " + sleepInfo,
                                                                   subtitle_align="right", subtitle=configInfo))
                    layout["lower"]["live1"].update(Panel("\n".join(liveInfo1), title=_("直播信息", "bold yellow") + f"({liveNumber}/{config.maxStream}) " + warningInfo,
                                                          title_align="left", style="bold yellow"))
                    layout["lower"]["live2"].update(Panel("\n".join(liveInfo2), style="bold yellow", title_align="left", title=modeInfo,
                                                          subtitle=_("请我喝一杯咖啡", "bold cyan") + ":https://github.com/Yudaotor", subtitle_align="right"))
                    layout["lower"]["info1"].update(Panel("\n".join(info1), subtitle=_("观看属地", "bold yellow") + ":" + watchRegion, subtitle_align="right", title=_("简略日志", "bold yellow"), title_align="left", style="bold yellow"))
                    layout["lower"]["info2"].update(
                        Panel("\n".join(info2), subtitle=_("(详细请见log文件)", "bold yellow"), subtitle_align="right", style="bold yellow", title_align="right",
                              title=_("代挂:闲鱼搜Khalilc", "bold yellow")))
                    sleep(1)
                    self.locks["refreshLock"].acquire()
                    if is_dockerized:
                        console.clear()
                    live.refresh()
                    if self.locks["refreshLock"].locked():
                        self.locks["refreshLock"].release()
        except Exception:
            log.error(_log("GUI线程异常"))
            print(_("GUI线程异常", "red"))
            log.error(formatExc(format_exc()))
