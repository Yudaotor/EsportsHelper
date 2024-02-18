from datetime import datetime

from EsportsHelper.I18n import i18n

_ = i18n.getText
_log = i18n.getLog


class Stats:
    def __init__(self):
        self.initDropsList = [" "]
        self.currentDropsList = [" "]
        self.initWatchHour = "-1"
        self.currentWatchHour = "-1"
        self.leaguesIdDict = {}
        self.lastDropCheckTime = int(datetime.now().timestamp() * 1e3)
        self.todayDrops = 0
        self.liveRegions = []
        self.lives = []
        self.lastCheckTime = ""
        self.nextCheckTime = ""
        self.status = _("初始化", color="yellow") + "[yellow]1[/yellow]"
        self.info = []
        self.banner = []
        self.sessionDropsDict = {}
        self.nextMatch = ""
        self.watchRegion = ""


stats = Stats()
