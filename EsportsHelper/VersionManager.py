import requests as req

from traceback import print_exc
from rich import print
from EsportsHelper.Logger import log


class VersionManager:
    CURRENT_VERSION = "1.2.1"

    @staticmethod
    def getLatestTag():
        try:
            latestTagResponse = req.get("https://api.github.com/repos/Yudaotor/EsportsHelper/releases/latest")
            if 'application/json' in latestTagResponse.headers.get('Content-Type', ''):
                latestTagJson = latestTagResponse.json()
                if "tag_name" in latestTagJson:
                    return str(latestTagJson["tag_name"][1:])
                return "0.0.0"
        except Exception as e:
            print("[red]从github获取最新版信息失败!")
            print_exc()
            return "0.0.0"

    @staticmethod
    def isLatestVersion(currentVersion):
        return currentVersion >= VersionManager.getLatestTag()

    @staticmethod
    def getVersion():
        return VersionManager.CURRENT_VERSION

    @staticmethod
    def checkVersion():
        if not VersionManager.isLatestVersion(VersionManager.getVersion()):
            log.warning("\n==!!! 新版本可用 !!!==\n ==请从此处下载: https://github.com/Yudaotor/EsportsHelper/releases/latest==")
            print("[yellow]\n==!!! 新版本可用 !!!==\n ==请从此处下载: https://github.com/Yudaotor/EsportsHelper/releases/latest ==[/yellow]")
