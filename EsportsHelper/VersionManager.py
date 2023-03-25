import traceback
import requests as req
from rich import print


class VersionManager:

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
            traceback.print_exc()
            return "0.0.0"

    @staticmethod
    def isLatestVersion(currentVersion):
        return currentVersion >= VersionManager.getLatestTag()
