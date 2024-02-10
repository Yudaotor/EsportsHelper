import json
from datetime import datetime, timezone
from traceback import format_exc

import cloudscraper

from EsportsHelper.Config import config
from EsportsHelper.I18n import i18n
from EsportsHelper.Logger import log
from EsportsHelper.Stats import stats
from EsportsHelper.Stream import Stream
from EsportsHelper.Utils import formatExc, matchStatusCode

_ = i18n.getText
_log = i18n.getLog
client = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    },
    debug=False)
client.get("https://lolesports.com/&lang=en")


def fetchWatchRegions():
    """
    Fetches the watch regions based on the country code obtained from Riot Games authentication API.

    Returns:
        str: The name of the country/region for watching, or "ERROR" if an exception occurs during the process.

    Notes:
        This function attempts to fetch the watch regions based on the country code obtained from the Riot Games
        authentication API. If successful, it returns the name of the country/region. If an exception occurs during
        the process, it logs the error and returns "ERROR".

    Raises:
        Any exceptions raised during the process are caught and logged, and "ERROR" is returned.
    """
    try:
        res = client.get("https://authenticate.riotgames.com/api/v1/login")
        if res.status_code != 200:
            log.error(_log("获取观看地区失败"))
            return "ERROR"
        resJson = res.json()
        country = resJson["country"]
        country_names = {
            "chn": _log("中国大陆"),
            "jpn": _log("日本"),
            "kor": _log("韩国"),
            "twn": _log("台湾"),
            "hkg": _log("香港"),
            "usa": _log("美国"),
            "sgp": _log("新加坡"),
            "tur": _log("土耳其"),
            "arg": _log("阿根廷"),
            "idn": _log("印度尼西亚"),
            "ita": _log("意大利"),
            "fra": _log("法国"),
            "mys": _log("马来西亚"),
            "deu": _log("德国"),
            "swe": _log("瑞典"),
            "nld": _log("荷兰"),
            "esp": _log("西班牙"),
            "bra": _log("巴西"),
            "rus": _log("俄罗斯"),
            "tha": _log("泰国"),
            "vnm": _log("越南"),
            "phl": _log("菲律宾"),
            "gbr": _log("英国"),
            "aus": _log("澳大利亚"),
            "can": _log("加拿大"),
            "mex": _log("墨西哥"),
            "chl": _log("智利"),
            "per": _log("秘鲁"),
            "col": _log("哥伦比亚"),
            "ecu": _log("厄瓜多尔"),
            "ury": _log("乌拉圭"),
        }
        return country_names.get(country, country)
    except Exception:
        log.error(_log("获取观看地区失败"))
        log.error(formatExc(format_exc()))
        # stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} API {_('获取观看地区失败', color='red')}")
        return "ERROR"


def fetchLiveMatches(ignoreBroadCast=True, ignoreDisWatchMatches=False):
    """
    Fetches live matches from the LoL Esports API.

    Args:
        ignoreBroadCast (bool, optional): Whether to ignore broadcast events. Defaults to True.
        ignoreDisWatchMatches (bool, optional): Whether to ignore matches not in the watch list. Defaults to False.

    Returns:
        list: A list of live matches.

    Notes:
        This function retrieves live matches from the LoL Esports API. It can optionally ignore broadcast events and
        matches not in the watch list. It returns a list of live matches.

    Raises:
        Exception: If an error occurs during the process, "ERROR" is returned.
    """
    try:
        headers = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = client.get("https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)
        if not matchStatusCode(200, res):
            log.error(_log("获取比赛列表失败"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('获取比赛列表失败', color='red')}")
        resJson = res.json()
        # with open("look.json", 'w') as f:
        #     json.dump(resJson, f)
        res.close()
        events = resJson["data"]["schedule"].get("events", [])
        liveList = []
        watchList = []
        if config.mode == "safe":
            watchList = ["worlds", "msi", "lcs", "lec", "lla", "vcs", "pcs", "lpl", "lck", "ljl-japan", "lco", "cblol-brazil", "tft_esports", "emea_masters"]
        elif config.onlyWatchMatches != [] and config.onlyWatchMatches != [""]:
            watchList = config.onlyWatchMatches
        for event in events:
            if ignoreDisWatchMatches and watchList != []:
                if event["league"]["slug"] not in watchList:
                    continue
            if ignoreBroadCast and event["type"] == "show" and event["league"]["slug"] != 'tft_esports' and event["league"]["slug"] != 'emea_masters':
                continue
            if len(event["streams"]) > 0:
                if event["type"] == "match":
                    slug = event["league"]["slug"]
                    strategy = event["match"]["strategy"]["type"] + " " + str(event["match"]["strategy"]["count"])
                    games = event["match"]["games"]
                    team1 = event["match"]["teams"][0]["code"]
                    team2 = event["match"]["teams"][1]["code"]
                    result1 = event["match"]["teams"][0]["result"]["gameWins"]
                    result2 = event["match"]["teams"][1]["result"]["gameWins"]
                    title = f"{team1} VS. {team2}  {result1} - {result2}"
                    gameNumber = next((game["number"] for game in games if game["state"] == "inProgress"), None)
                    if gameNumber is None:
                        gameNumber = sum(1 for game in games if game["state"] == "completed")

                    liveList.append(slug)
                    # find stream and update
                    stream = next((stream for stream in stats.lives if stream.league == slug.upper()), None)
                    if stream is not None:
                        stream.gameNumber = gameNumber
                        stream.strategy = strategy
                        stream.title = title
                    else:
                        stats.lives.append(
                            Stream(league=slug.upper(), gameNumber=gameNumber, strategy=strategy,
                                   title=title, provider="", url="", viewers="", status="notReady"))

                elif event["type"] == "show":
                    slug = event["league"]["slug"]
                    liveList.append(slug)
                    # Find the stream in the list
                    stream = next((s for s in stats.lives if s.league == slug.upper()), None)
                    if stream:
                        # Stream found, update its attributes
                        stream.gameNumber = _log("转播")
                        stream.strategy = _log("转播")
                        stream.title = "None"
                    else:
                        # Stream not found, create a new one and append it to the list
                        stats.lives.append(
                            Stream(league=slug.upper(), gameNumber=_log("转播"), strategy=_log("转播"),
                                   title="None", provider="", url="", viewers="", status="notReady"))

        return liveList
    except Exception:
        log.error("API " + _log("获取比赛列表失败"))
        log.error(formatExc(format_exc()))
        # stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} API {_('获取比赛列表失败', color='red')}")
        liveList = ["ERROR"]
        return liveList


def checkNextMatch():
    """
    Checks the schedule for the next upcoming match.

    Returns:
        bool: True if the next match is successfully found, False otherwise.

    Notes:
        This function retrieves the schedule of upcoming events from the LoL Esports API and checks for the next
        unstarted match. If found, it updates the `stats.nextMatch` attribute with the name of the league and the
        start time of the match in a nice format ('%m-%d %H:%M'). Returns True if the next match is found and
        False otherwise.
    """
    try:
        watchList = []
        headers = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        getScheduleUrl = "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB"
        if config.mode == "safe":
            getScheduleUrl = "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-US&leagueId=98767991299243165%2C98767991332355509%2C98767991310872058%2C105709090213554609%2C98767991302996019%2C98767991349978712%2C101382741235120470%2C98767991314006698%2C104366947889790212%2C107213827295848783%2C110988878756156222%2C98767991325878492%2C98767975604431411%2C98767991295297326%2C100695891328981122%2C105266094998946936%2C108001239847565215"
            watchList = ["worlds", "msi", "lcs", "lec", "lla", "vcs", "pcs", "lpl", "lck", "ljl-japan", "lco", "cblol-brazil", "tft_esports", "emea_masters"]
        elif config.onlyWatchMatches != [] and config.onlyWatchMatches != [""]:
            watchList = config.onlyWatchMatches
        res = client.get(getScheduleUrl, headers=headers)
        if not matchStatusCode(200, res):
            log.error(_log("获取下一场比赛时间失败"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('获取下一场比赛时间失败', color='red')}")
            return False
        resJson = res.json()
        # with open("look.json", 'w') as f:
        #     json.dump(resJson, f)
        res.close()
        events = resJson["data"]["schedule"]["events"]
        for event in events:
            if event["state"] == "unstarted":
                if watchList:
                    if event["league"]["slug"] in watchList:
                        startTime = datetime.strptime(event["startTime"], '%Y-%m-%dT%H:%M:%SZ')
                        currentTimeString = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                        currentTime = datetime.strptime(currentTimeString, '%Y-%m-%dT%H:%M:%SZ')
                        if currentTime < startTime:
                            timeDiff = startTime - currentTime
                            systemTimeDT = getSystemTime()
                            startTime = systemTimeDT + timeDiff
                            niceStartTime = datetime.strftime(startTime, '%m-%d %H:%M')
                            stats.nextMatch = event["league"]["name"] + "|" + niceStartTime
                            return True
                        else:
                            continue
                    else:
                        continue

                else:
                    startTime = datetime.strptime(event["startTime"], '%Y-%m-%dT%H:%M:%SZ')
                    currentTimeString = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                    currentTime = datetime.strptime(currentTimeString, '%Y-%m-%dT%H:%M:%SZ')
                    if currentTime < startTime:
                        timeDiff = startTime - currentTime
                        systemTimeDT = getSystemTime()
                        startTime = systemTimeDT + timeDiff
                        niceStartTime = datetime.strftime(startTime, '%m-%d %H:%M')
                        stats.nextMatch = event["league"]["name"] + "|" + niceStartTime
                        return True
                    else:
                        continue
            startTime = datetime.strptime(events[-1]["startTime"], '%Y-%m-%dT%H:%M:%SZ')
            currentTimeString = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            currentTime = datetime.strptime(currentTimeString, '%Y-%m-%dT%H:%M:%SZ')
            if currentTime < startTime:
                timeDiff = startTime - currentTime
                systemTimeDT = getSystemTime()
                startTime = systemTimeDT + timeDiff
                niceStartTime = datetime.strftime(startTime, '%m-%d %H:%M')
                stats.nextMatch = events[-1]["league"]["name"] + "|" + niceStartTime
        return True
    except Exception:
        log.error("API " + _log("获取下一场比赛时间失败"))
        log.error(formatExc(format_exc()))
        # stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} API {_('获取下一场比赛时间失败', color='red')}")
        return False


def getSystemTime() -> datetime:
    """
    Retrieves the current system time as a datetime object.

    Returns:
        datetime: The current system time.

    Notes:
        This function obtains the current system time and converts it into a datetime object in the UTC timezone,
        formatted as '%Y-%m-%dT%H:%M:%SZ'.
    """
    systemTimeStr = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    systemTimeDT = datetime.strptime(systemTimeStr, '%Y-%m-%dT%H:%M:%SZ')
    return systemTimeDT

# fetchLiveMatches()
# fetchTimeUntilNextMatch()
