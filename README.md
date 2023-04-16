<p align="center">
<a href="https://github.com/Yudaotor/EsportsHelper"><img alt="EsportsHelper" src="https://i.328888.xyz/2023/03/28/itMRQF.png"></a><br/>
<a href="https://lolesports.com"><img alt="lolesports" src="https://img.shields.io/badge/WebSite-lol%20esports-445fa5.svg?style=plastic"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Yudaotor/EsportsHelper"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/pulls"><img alt="PRWelcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat"></a><br/>
<a href="https://www.cdnjson.com/images/2023/03/13/image-merge-1678713037835.png"><img alt="buymecoffee" src="https://user-images.githubusercontent.com/87225219/228188809-9d136e10-faa1-49b9-a6b7-b969dd1d8c7f.png"></a>
</p>

**Language**: [English](https://github.com/Yudaotor/EsportsHelper/blob/main/README.EN.md)|[Chinese](https://github.com/Yudaotor/EsportsHelper/blob/main/README.md)
# 电竞助手 EsportsHelper
通过selenium模拟浏览器来自动观看电竞比赛,网址:[lolesports](lolesports.com)  
至于会不会被拳头检测到这个问题,目前还没有答案.  
哦对了,用的是谷歌浏览器哦 （必须要下一个最新版的谷歌浏览器哦）  
来自中国大陆的需搭配VPN使用  
**如何下载**:点击右侧的[release](https://github.com/Yudaotor/EsportsHelper/releases)下载
## 联系我
使用过程中有遇到什么问题或者建议可以在github上提出issue  
或者加TG群交流: https://t.me/+0PjLPCy_IIJhNzM1  
或者可以联系我  
discord: Khalil#7843  
可以给我点个小星星吗(*^_^*)⭐  
## 界面
![image](https://user-images.githubusercontent.com/87225219/228434642-6b7317e5-1c0a-4931-b358-f6e2b304429b.png)

## 运行平台  
windows,linux  

### linux  
如何在linux中运行请点击右侧查看教程[linux教程](https://github.com/Yudaotor/EsportsHelper/wiki/%E5%A6%82%E4%BD%95%E5%9C%A8linux%E7%8E%AF%E5%A2%83%E8%BF%90%E8%A1%8C%EF%BC%88run-in-linux%EF%BC%89)
### mac
暂时运行方法：
```shell
python -m pip install -r requirements.txt
./run_job.sh 0
```


## 特性
1. 自动打开浏览器,进入lolesports.com,查询哪些赛区在进行比赛(在放录播的赛区会被忽视),进入观看并设置为最低清晰度(为了节省流量)
2. 可以自行设置是否选择无头模式(默认关闭)(无头模式即headless,开启后浏览器会不可见,在后台运行,缓解电脑CPU压力)
3. 可以自行设置不观看哪些赛区的比赛.(默认为空)(注意,此处是包含关系的逻辑,举例:当你设置了lck以后,lck_challengers同样不会观看)(建议设置,避免观看所有比赛从而被检测)
4. 可以自行设置多久来查询一次比赛最新信息.(默认600秒)(关闭已经结束的比赛和开启新开始的比赛)
5. 掉落提醒(支持钉钉,Discord,饭碗警告)(不是所有掉落都会被提醒,拳头的锅,有时候网页上不会出现弹窗)
6. 软件发生错误时可以发送错误提醒
7. 可以设置最长运行时间，到达时间后关闭软件  
8. 可以设置休眠时间段，在时间段内软件会以1小时为间隔来检查
9. 可以设置桌面提醒（尚未测试,不确定是否生效）
10. 可以手动添加代理(绝大部分用户无需配置)
11. 可以设置删除视频流元素(节省流量)(风险未知,有兴趣自行尝试) 
12. 可以查看程序本次运行得到的掉落数以及掉落赛区信息
13. 可以通过本地浏览器缓存免账密登录
14. 可以自定义谷歌浏览器的地址(支持绿色版即免安装版)

## 配置信息
config.yaml
```yaml
### 必填项
username: "账号用户名"        # 必填，账号  
password: "密码"  # 必填，密码  
### 选填项
delay: 600                    # 每次检查的时间间隔，单位为秒(默认为600秒)(每次检测时间会在你设置的时延0.8-1.5倍之间随机波动)  
headless: False              # 设置为True时，程序会在后台运行，否则会打开浏览器窗口(默认为False)  
disWatchMatches: ["lck", "lpl", "lcs"] # 不想看的赛区名称，可以在这里添加.(注意,是小写)  
maxRunHours: -1                  # 负值为一直运行，正值为运行小时, 默认-1
proxy: "你的代理地址" # 代理地址，选填，一般用户不用填。 e.g., "socks://127.0.0.1:20173"
connectorDropsUrl: "你的webhook链接"   # (支持钉钉,Discord,饭碗警告)具体配置方法见此处https://github.com/Yudaotor/EsportsHelper/wiki/%E6%80%8E%E4%B9%88%E9%85%8D%E7%BD%AE%E6%8E%89%E8%90%BD%E6%8F%90%E9%86%92%3F(%E5%8A%9F%E8%83%BD%E5%BE%85%E6%B5%8B%E8%AF%95
platForm: "windows"    # 使用平台,默认为windows,如需使用linux请在此处进行配置  
closeStream: "False"   # 省流模式，默认False，关闭直播间的视频流（未知风险）（有兴趣者自行尝试） 
desktopNotify: "False"  # 系统弹窗提示，默认False
sleepPeriod: "8-13" # 休眠时间段，（默认为空）格式为"开始小时-结束小时",在休眠时间段中会以1小时间隔来检查。区间为左闭合右开。
ignoreBoardCast: True    # 设置为否会提前进入直播间，以及将支持某些一直处于转播的赛区直播
userDataDir: "C:\\Users\\Khalil\\AppData\\Local\\Google\\Chrome\\User Data"  # 例子,其中Khalil处改为自己电脑的名字,具体教程见https://github.com/Yudaotor/EsportsHelper/wiki/%E6%80%8E%E4%B9%88%E4%BD%BF%E7%94%A8%E6%9C%AC%E5%9C%B0%E6%B5%8F%E8%A7%88%E5%99%A8%E7%BC%93%E5%AD%98-%E5%85%8D%E8%B4%A6%E5%AF%86%E7%99%BB%E5%BD%95
chromePath: "谷歌浏览器自订路径"
countDrops: True     #是否检查掉落数
```

### 不观看赛区的配置详解:
注意,此处是包含关系的逻辑,举例:当你设置了lck以后,lck_challengers同样不会观看  
可以设置一些赛区不观看,防止出现24小时观赛的情况  
具体赛区名字可以见以下说明:  
lpl:lpl  
lck:lck  
lck_challengers_league:lck_challengers_league  
lec:lec  
lcs:lcs  
lco:lco  
vcs:vcs  
cblol:cblol  
cblol_academy:cblol_academy  
lla:lla  
ljl:ljl-japan  
ljl_academy:ljl_academy  
cblol-brazil:cblol-brazil  
pcs:pcs  
honor_division:honor_division  
volcano_discover_league:volcano_discover_league  
hitpoint_masters:hitpoint_masters  
worlds:worlds  
european-masters:european-masters  
golden_league:movistar_fiber_golden_league  
honor_league:honor_league  
tcl:turkiye-sampiyonluk-ligi
nlc:nlc  
elite_series:elite_series  
superliga:superliga  
greek_legends:greek_legends  
primeleague:primeleague  
liga_master:liga_master_flo  
ultraliga:ultraliga  
claro_gaming_stars_league:claro_gaming_stars_league  
arabian_league:arabian_league  
lfl:lfl  
## by the way
本项目思路及部分代码来自Poro，感谢。[此处](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer)
