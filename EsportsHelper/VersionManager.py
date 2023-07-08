from traceback import format_exc
import requests as req
from EsportsHelper.Config import config
from rich import print
from EsportsHelper.Logger import delimiterLine
from EsportsHelper.Logger import log
from EsportsHelper.I18n import i18n
from EsportsHelper.Stats import stats

_ = i18n.getText
_log = i18n.getLog
LATEST_URL = "https://github.com/Yudaotor/EsportsHelper/releases/latest"


def getLatestVersion():
    """
    Get the latest version number of the EsportsHelper project on GitHub.

    Returns:
        str: The latest version number. If the fetch fails, "0.0.0" is returned.
    """
    try:
        latestTagResponse = req.get(
            "https://api.github.com/repos/Yudaotor/EsportsHelper/releases/latest")
        if 'application/json' in latestTagResponse.headers.get('Content-Type', ''):
            latestTagJson = latestTagResponse.json()
            if "tag_name" in latestTagJson:
                return str(latestTagJson["tag_name"][1:])
            log.error(_log("当前IP地址获取最新版本过于频繁, 请过段时间再试"))
            log.error(latestTagJson["message"])
            return "0.0.0"
    except Exception:
        stats.info.append(_("获取最新版本失败", color="red"))
        modifiedTrace = f"{50 * '+'}\n"
        lines = format_exc().splitlines()
        for line in lines:
            if "Stacktrace:" in line:
                break
            modifiedTrace += line + '\n'
        log.error(modifiedTrace)
        return "0.0.0"


def checkVersion():
    """
    Check whether there is a new version available for EsportsHelper.

    :return: None
    """
    versionNow = VersionManager.getVersion()
    versionLatest = getLatestVersion()
    if versionNow < versionLatest:
        stats.info.append(_("当前版本: ", color="yellow") + versionNow + "|"
                          + _("最新版本: ", color="yellow") + versionLatest +
                          _("\n==!!! 新版本可用 !!!==\n===下载:", color="yellow") + f"{LATEST_URL}")
        log.warning(_log("\n==!!! 新版本可用 !!!==\n===下载:") + LATEST_URL)


class VersionManager:
    def __init__(self) -> None:
        pass

    @staticmethod
    def getVersion():
        """
        Gets the current version number
        :return: str，version number
        """
        return config.version
