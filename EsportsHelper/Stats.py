
from EsportsHelper.I18n import i18n

_ = i18n.getText
_log = i18n.getLog


class Stats:
    def __init__(self):
        self.historyDrops = 0
        self.totalWatchHours = 0
        self.todayDrops = 0
        self.dropsDict = {}
        self.sessionDrops = 0
        self.liveRegions = []
        self.lives = []
        self.lastCheckTime = ""
        self.nextCheckTime = ""
        self.status = _("初始化", color="yellow") + "[yellow]1[/yellow]"
        self.info = []
        self.banner = []
        self.sessionDropsDict = {}
        self.nextMatch = ""


stats = Stats()
