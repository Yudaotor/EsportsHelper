from traceback import format_exc

import requests as req
from EsportsHelper.Logger import log
from rich import print


class VersionManager:
    CURRENT_VERSION = "1.6.1"

    @staticmethod
    def getLatestTag():
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
                return "0.0.0"
        except Exception:
            print("[red]Get Newest Version Failed")
            log.error(format_exc())
            return "0.0.0"

    @staticmethod
    def isLatestVersion(currentVersion):
        """
        Checks if the current version is the latest available version.

        Args:
        - currentVersion (str): The current version to compare with the latest available version.

        Returns:
        - bool: True if the current version is the latest, False otherwise.
        """
        return currentVersion >= VersionManager.getLatestTag()

    @staticmethod
    def getVersion():
        """
        Gets the current version number
        :return: str，version number
        """
        return VersionManager.CURRENT_VERSION

    @staticmethod
    def checkVersion():
        """
        Check whether there is a new version available for EsportsHelper.

        :return: None
        """
        if not VersionManager.isLatestVersion(VersionManager.getVersion()):
            log.warning(
                f"\n==!!! NEW VERSION AVAILABLE !!!==\n ==DownLoad: https://github.com/Yudaotor/EsportsHelper/releases/latest")
            print("[yellow]\n==!!! NEW VERSION AVAILABLE !!!==\n ==DownLoad: https://github.com/Yudaotor/EsportsHelper/releases/latest ==[/yellow]")
            log.warning(
                f"\n==!!! 新版本可用 !!!==\n ==下载: https://github.com/Yudaotor/EsportsHelper/releases/latest")
            print("[yellow]\n==!!! 新版本可用 !!!==\n ==下载: https://github.com/Yudaotor/EsportsHelper/releases/latest ==[/yellow]")
