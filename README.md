<p align="center">
<a href="https://github.com/Yudaotor/EsportsHelper"><img alt="EsportsHelper" src="https://github.com/Yudaotor/EsportsHelper/assets/87225219/79896860-f119-4e69-bac7-148504d4c2ae"></a><br/>
<a href="https://lolesports.com"><img alt="lolesports" src="https://img.shields.io/badge/WebSite-lol%20esports-445fa5.svg?style=plastic"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Yudaotor/EsportsHelper"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/pulls"><img alt="PRWelcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat"></a><br/>
<a href="https://www.cdnjson.com/images/2023/03/13/image-merge-1678713037835.png">点它-><img alt="buymecoffee" src="https://user-images.githubusercontent.com/87225219/228188809-9d136e10-faa1-49b9-a6b7-b969dd1d8c7f.png"></a>
</p>

**Language**: [English](https://github.com/Yudaotor/EsportsHelper/blob/main/README.EN.md) | [Chinese](https://github.com/Yudaotor/EsportsHelper/blob/main/README.md) | [Spanish](https://github.com/Yudaotor/EsportsHelper/blob/main/README.ES.md)
# 电竞助手 EsportsHelper
通过selenium模拟浏览器来自动观看电竞比赛,网址: [LolEsports](lolesports.com)  
**避免被拳头检测,请尽量过滤掉小赛区(打开安全模式即可)(以及不要同时观看超过5个比赛!!!!)**  
哦对了,用的是谷歌浏览器哦 （必须要下一个最新版本谷歌浏览器哦）  
**来自中国大陆的需搭配VPN使用**  
**如何下载**:点击右侧的[Releases](https://github.com/Yudaotor/EsportsHelper/releases)下载
## 联系我
使用过程中有遇到什么问题或者建议可以在Github上提出issue  
或者加TG群交流: https://t.me/+0PjLPCy_IIJhNzM1  
或者可以联系我  
Discord: Khalil#7843  
可以给我点个小星星吗(*^_^*)⭐  
## 不想自己挂?  
可以找我代挂 Q群:553984868  闲鱼: Khalilc
## 界面
![image](https://github.com/Yudaotor/EsportsHelper/assets/87225219/ec3603e5-463c-4a57-b09a-0c34e90522da)


## 运行平台  
Windows, Linux  

### Linux  
如何在Linux中运行请点击右侧查看教程[Linux教程](https://github.com/Yudaotor/EsportsHelper/wiki/%E5%A6%82%E4%BD%95%E5%9C%A8linux%E7%8E%AF%E5%A2%83%E8%BF%90%E8%A1%8C%EF%BC%88run-in-linux%EF%BC%89)
### Mac
暂时运行方法：
```shell
python -m pip install -r requirements.txt
./run_job.sh 0
```

## 在Docker中运行
要使用我们的（非官方）Docker 版本，可以使用我们的 "docker-compose.yml "文件。只需将该文件与配置文件 "config.yml"（可以使用我们的配置文件生成器）一起放在需要的位置，然后运行 "sudo docker compose up -d "即可。别忘了，配置文件中的 "isDockerized "变量必须设置为 "True"。请注意，该应用程序使用的是真正的浏览器（Chromium/Chrome），这意味着它可能会占用高达 2 GB 的内存。Docker仓库地址: https://hub.docker.com/r/redr00t/esportshelper  

## 关于多开  
压缩包解压多个文件夹,然后各自不同的配置文件多开即可实现 或者你也可以使用Docker来实现多开.


## 特性
1. 自动打开浏览器,进入lolesports.com,查询哪些赛区在进行比赛(在放赛前等待的赛区会被忽视,但是可以通过ignoreBroadCast配置从而不忽视),进入观看并设置为最低清晰度(为了节省流量)
2. 可以自行设置是否选择无头模式(默认关闭)(无头模式即headless,开启后浏览器会不可见,在后台运行,缓解电脑CPU压力)
3. 可以自行设置**不观看哪些赛区** **或者只观看**的比赛.(默认为空)(注意,不观看是包含关系的逻辑,举例:当你设置了lck以后,lck_challengers同样不会观看)(只观看是严格匹配的逻辑)(建议设置,避免观看所有比赛从而被检测)
4. 可以自行设置多久来查询一次比赛最新信息.(默认600秒)(关闭已经结束的比赛和开启新开始的比赛)
5. **掉落提醒**(支持钉钉,Discord,饭碗警告,企业微信,飞书)
6. 软件发生错误时可以发送错误提醒(推送信息类型支持筛选)
7. 可以设置最长运行时间，到达时间后自动关机(只有windows会自动关机)  
8. 可以设置多段休眠时间段，在休眠时间段中会关闭观赛网页,待休眠结束后重新打开.
9. 可以设置桌面提醒.
10. 可以手动添加代理.(绝大部分用户无需配置)
11. 省流模式,可以删除视频流元素(节省流量)(风险存在,有被拳头检测可能) 
12. 可以查看程序本次运行得到的掉落数以及掉落赛区信息.
13. 可以通过本地浏览器缓存免账密登录.
14. 可以自定义谷歌浏览器的地址.(支持绿色版即免安装版)
15. 可以配置语言,目前支持**简体中文**,**繁体中文**,**英语**和**西班牙语**.
16. 可以配置是否**自动休眠**,即当没有比赛时关闭页面,直到比赛重新打开.(**推荐**设置)
17. 非自动休眠模式下如检测到距离下场比赛时间较长也会进行以1小时间隔检查.
18. 可以设定**最大同时观看直播数**,避免同时观看过多赛区被拳头检测.
19. 可以导出生涯掉落详细信息.
20. 可以打开**安全模式**,自动过滤小赛区 防止被检测.
21. 可以显示双方对局比分信息.
22. 支持ARM64.
23. 支持Docker环境.


## 配置信息
config.yaml
```yaml
### 必填项
username: "账号用户名"                         # 必填，账号  
password: "密码"                              # 必填，密码  
### 选填项
delay: 600                                    # 每次检查的时间间隔，单位为秒(默认为600秒)(每次检测时间会在你设置的时延0.8-1.5倍之间随机波动)  
headless: False                               # 设置为True时，程序会在后台运行，否则会打开浏览器窗口(默认为False)  
language: "zh_CN"                             # 现支持语言"zh_CN","zh_TW","en_US".简体中文,繁体中文,英语.
nickName: ""                                  # 绰号,为空时默认为username.(增强隐私)  
onlyWatchMatches: ["lcs","lla","lpl","lck","ljl-japan","lco","lec","cblol-brazil","pcs","tft_esports","worlds","wqs"]   # 只观看的赛区名称,小写.
disWatchMatches: ["prime","lfl","liga","hitpoint","series","nlc","nationals","academy","qualifiers","legends","challengers","league"]        # 不想看的赛区名称，可以在这里添加.(注意,是小写)  
maxRunHours: -1                               # 负值为一直运行，正值为运行小时, 默认-1
maxStream: 4                                  # 默认值为4,最大同时观看的比赛数,超过将会不予观看.
mode: "safe"                                  # 模式选择，safe为安全模式，normal为普通模式，默认为safe.具体含义见github 
exportDrops: False                            # 默认为False,是否需要导出生涯掉落详情文件,只会在脚本打开时生成.
briefLogLength: 10                            # 日志简略信息条数.默认为10
proxy: "你的代理地址"                          # 代理地址，选填，一般用户不用填,除非你知道你在干什么。 例子, "socks://127.0.0.1:20173"
connectorDropsUrl: "你的webhook链接"           # (支持钉钉,Discord,饭碗警告,企业微信,飞书)具体配置方法见此处https://github.com/Yudaotor/EsportsHelper/wiki/%E6%80%8E%E4%B9%88%E9%85%8D%E7%BD%AE%E6%8E%89%E8%90%BD%E6%8F%90%E9%86%92%3F
platForm: "windows"                           # 使用平台,默认为Windows,如需使用Linux请在此处进行配置  
closeStream: False                            # 省流模式，默认False，关闭直播间的视频流(风险存在,有被拳头检测可能) 
desktopNotify: False                          # 系统右下角弹窗提示，默认False
sleepPeriod: ["8-13", "20-23"]                # 休眠时间段，（默认为空）格式为"开始小时-结束小时",在休眠时间段中会关闭观赛网页,待休眠结束后重新打开。区间为左闭合右开。
ignoreBroadCast: True                         # 设置为False会提前进入直播间，以及将支持某些一直处于转播的赛区直播(例如TFT)
userDataDir: "C:\\Users\\xxxxx\\AppData\\Local\\Google\\Chrome\\User Data"  # 例子,其中xxxxx处改为自己电脑的名字,具体教程见https://github.com/Yudaotor/EsportsHelper/wiki/%E6%80%8E%E4%B9%88%E4%BD%BF%E7%94%A8%E6%9C%AC%E5%9C%B0%E6%B5%8F%E8%A7%88%E5%99%A8%E7%BC%93%E5%AD%98-%E5%85%8D%E8%B4%A6%E5%AF%86%E7%99%BB%E5%BD%95
chromePath: "X:\\xxxxx\\xx\\Chrome.exe"       # 谷歌浏览器自订路径
countDrops: True                              # 是否检查掉落数
notifyType: "all"                             # 推送信息的类型筛选,"all"为所有信息推送,"error"为仅推送报错信息,"drops"为仅推送掉落信息
autoSleep: True                               # (推荐)是否自动休眠,默认True
debug: False                                  # 是否开启debug模式,开启后在发生异常时会截屏到pics文件夹下,默认False
arm64: False                                  # 支持在Linux ARM64使用Chromium,需要同时配置platForm: "linux" 并且要有 chromedriver 在路径: "/home/USERNAME/.local/share/undetected_chromedriver/chromedriver", 更多细节见: https://github.com/Yudaotor/EsportsHelper/wiki/The-Way-Using-Chromium-on-ARM64
isDockerized: False                           # 只有当在Docker中运行时 配置为True,默认为False.
```

### 不观看赛区的配置详解:
注意,此处是包含关系的逻辑,举例:当你设置了lck以后,lck_challengers同样不会观看  
可以设置一些赛区不观看,比如次级联赛等(掉落率很低)(推荐)  
具体赛区名字可以见以下说明(冒号后的即为在配置中输入的赛区名)(注意是小写):  
Worlds Qualifying Series:wqs  
LPL:lpl  
LCK:lck  
LCK_CHALLENGERS_LEAGUE:lck_challengers_league  
LEC:lec  
LCS:lcs  
TFT:tft_esports  
LCS_CHALLENGERS:north_american_challenger_league  
LCS_CHALLENGERS_QUALIFIERS:lcs_challengers_qualifiers  
LCO:lco  
VCS:vcs  
MSI:msi  
WORLDS:worlds  
CBLOL:cblol-brazil  
CBLOL_ACADEMY:cblol_academy  
LLA:lla  
LJL:ljl-japan  
LJL_ACADEMY:ljl_academy   
EMEA:european-masters  
PCS:pcs  
La Ligue Française:lfl  
NLC:nlc  
HONOR_DIVISION:honor_division  
VOLCANO_DISCOVER_LEAGUAGE:volcano_discover_league  
HITPOINT_MASTERS:hitpoint_masters  
GOLDEN_LEAGUE:movistar_fiber_golden_league  
HONOR_LEAGUE:honor_league  
TCL:turkiye-sampiyonluk-ligi  
ELITE_SERIES:elite_series  
SUPERLIGA:superliga  
ULTRALIGA:ultraliga  
GREEK_LEAGUE:greek_legends  
PRIMELEAGUE:primeleague  
LIGA_MASTER:liga_master_flo  
LIGA_PORTUGUESA:liga_portuguesa  
CLARO_GAMING_STARS_LEAGUE:claro_gaming_stars_league  
ARABIAN_LEAGUE:arabian_league  
NORTH_REGIONAL_LEAGUE:north_regional_league  
SOUTH_REGIONAL_LEAGUE:south_regional_league  
PG_NATIONALS:pg_nationals  
King's Duel:duelo_de_reyes  

## By the way
本项目思路及部分代码来自Poro，感谢。[此处](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer)
