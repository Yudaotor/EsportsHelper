from traceback import format_exc
import requests as req
from EsportsHelper.Logger import log
from rich import print
from EsportsHelper.I18n import _, _log


class VersionManager:
    def __init__(self, config) -> None:
        self.language = config.language

    def getLatestVersion(self):
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
                print(_("获取最新版本过于频繁, 请过段时间再试", color="red", lang=self.language))
                log.error(latestTagJson["message"])
                return "0.0.0"
        except Exception:
            print(_("获取最新版本失败", color="red", lang=self.language))
            log.error(format_exc())
            return "0.0.0"

    @staticmethod
    def getVersion():
        """
        Gets the current version number
        :return: str，version number
        """
        return "1.6.1"

    def checkVersion(self):
        """
        Check whether there is a new version available for EsportsHelper.

        :return: None
        """
        versionNow = VersionManager.getVersion()
        versionLatest = VersionManager.getLatestVersion(self)
        if versionNow < versionLatest:
            print(_("当前版本: ", color="yellow", lang=self.language), end="")
            print(versionNow, end="")
            print(_("最新版本: ", color="yellow", lang=self.language), end="")
            print(versionLatest)
            print(_("\n==!!! 新版本可用 !!!==\n ===下载:", color="yellow", lang=self.language), end="")
            print("https://github.com/Yudaotor/EsportsHelper/releases/latest ==\n")
            log.warning(_log("\n==!!! 新版本可用 !!!==\n ===下载:", lang=self.language), end="")
            log.warning("https://github.com/Yudaotor/EsportsHelper/releases/latest ==\n")
