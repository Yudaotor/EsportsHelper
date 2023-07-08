from traceback import format_exc

from EsportsHelper.I18n import i18n
from EsportsHelper.Logger import log

_ = i18n.getText
_log = i18n.getLog


class Stream:
    def __init__(self, provider, league, url, viewers, status, gameNumber="", strategy="", title="None", definition="Auto"):
        self.provider = provider
        self.league = league
        self.title = title
        self.url = url
        self.viewers = viewers
        self.status = status
        self.strategy = strategy
        self.gameNumber = gameNumber
        self.definition = definition

    def show(self):
        try:
            if self.gameNumber == _log("转播") or self.strategy == _log("转播"):
                status = _log("转播")
            else:
                status = "(" + str(self.gameNumber) + "/" + self.strategy.upper() + ")"

            statusColor = "bold yellow"
            leagueColor = "bold magenta"
            viewersColor = "bold cyan"
            titleColor = "bold green"

            if self.status == "online":
                viewersText = f"{_('观看人数: ', color=statusColor)}[{viewersColor}]{self.viewers}[/{viewersColor}]"
                titleText = f"{_('标题: ', color=statusColor)}[{titleColor}]{self.title}[/{titleColor}] {status}"
                leagueText = f"{_('赛区: ', color=statusColor)}[{leagueColor}]{self.league}[/{leagueColor}]"
                statusText = f"{_('状态: ', color=statusColor)}{status}"
                definitionText = f"{_('清晰度: ', color=statusColor)}[{titleColor}]{self.definition}[/{titleColor}]"

                if self.viewers.isdigit():
                    if self.title != "None":
                        return f"{leagueText} {viewersText} {definitionText}\n{titleText}"
                    else:
                        return f"{leagueText} {viewersText} {definitionText}\n{statusText}"
                else:
                    if self.title != "None":
                        return f"{leagueText} {definitionText}\n{titleText}"
                    else:
                        return f"{leagueText} {definitionText}\n{statusText}"
            elif self.status == "offline":
                return f"[{leagueColor}]{self.league}[/{leagueColor}] {_('比赛结束 等待关闭', color='yellow')}"
            elif self.status == "retry":
                return f"[{leagueColor}]{self.league}[/{leagueColor}] {_('观看异常 待重试', color='red')}"
            elif self.status == "error":
                return f"[{leagueColor}]{self.league}[/{leagueColor}] {_('观看异常', color='red')}"
            return ""
        except Exception:
            log.error(format_exc())
            return ""

    def log(self):
        try:
            if self.gameNumber == _log("转播") or self.strategy == _log("转播"):
                status = _log("转播")
            else:
                status = "(" + str(self.gameNumber) + "/" + self.strategy.upper() + ")"

            leagueText = f"{_log('赛区: ')}{self.league}"
            viewersText = f"{_log('观看人数: ')}{self.viewers}"
            titleText = f"{_log('标题: ')}{self.title} {status}"
            statusText = f"{_log('状态: ')}{status}"
            definitionText = f"{_log('清晰度: ')}{self.definition}"

            if self.status == "online":
                if self.viewers.isdigit():
                    if self.title != "None":
                        return f"\n{leagueText} {viewersText} {definitionText}\n{titleText}"
                    else:
                        return f"\n{leagueText} {viewersText} {definitionText}\n{statusText}"
                else:
                    if self.title != "None":
                        return f"\n{leagueText} {definitionText}\n{titleText}"
                    else:
                        return f"\n{leagueText} {definitionText}\n{statusText}"
            elif self.status == "offline":
                return f"{self.league} {_log('比赛结束 等待关闭')}"
            elif self.status == "retry":
                return f"{self.league} {_log('观看异常 待重试')}"
            elif self.status == "error":
                return f"{self.league} {_log('观看异常')}"
            return ""
        except Exception:
            log.error(format_exc())
            return ""

