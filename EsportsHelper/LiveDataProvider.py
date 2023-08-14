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


def fetchLiveMatches(ignoreBroadCast=True, ignoreDisWatchMatches=False):
    try:
        headers = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = client.get("https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)
        if not matchStatusCode(200, res):
            log.error(_log("获取比赛列表失败"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('获取比赛列表失败', color='red')}")
        resJson = res.json()
        # with open("live.json", 'w') as f:
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
    try:
        watchList = []
        if config.mode == "safe":
            watchList = ["worlds", "msi", "lcs", "lec", "lla", "vcs", "pcs", "lpl", "lck", "ljl-japan", "lco", "cblol-brazil", "tft_esports", "emea_masters"]
        elif config.onlyWatchMatches != [] and config.onlyWatchMatches != [""]:
            watchList = config.onlyWatchMatches
        headers = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = client.get("https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB", headers=headers)
        if not matchStatusCode(200, res):
            log.error(_log("获取下一场比赛时间失败"))
            stats.info.append(f"{datetime.now().strftime('%H:%M:%S')} {_('获取下一场比赛时间失败', color='red')}")
            return False
        resJson = res.json()
        # with open("schdue.json", 'w') as f:
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
    systemTimeStr = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    systemTimeDT = datetime.strptime(systemTimeStr, '%Y-%m-%dT%H:%M:%SZ')
    return systemTimeDT

# fetchLiveMatches()
# fetchTimeUntilNextMatch()
