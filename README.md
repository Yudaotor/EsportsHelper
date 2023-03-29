<p align="center">
<a href="https://github.com/Yudaotor/EsportsHelper"><img alt="EsportsHelper" src="https://i.328888.xyz/2023/03/28/itMRQF.png"></a><br/>
<a href="https://lolesports.com"><img alt="lolesports" src="https://img.shields.io/badge/WebSite-lol%20esports-445fa5.svg?style=plastic"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Yudaotor/EsportsHelper"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/pulls"><img alt="PRWelcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat"></a><br/>
<a href="https://www.cdnjson.com/images/2023/03/13/image-merge-1678713037835.png"><img alt="buymecoffee" src="https://user-images.githubusercontent.com/87225219/228188809-9d136e10-faa1-49b9-a6b7-b969dd1d8c7f.png"></a>
</p>


# 电竞助手 EsportsHelper
通过selenium模拟浏览器来自动观看电竞比赛,网址:[lolesports](lolesports.com)  
至于会不会被拳头检测到这个问题,目前还没有答案.  
哦对了,用的是谷歌浏览器哦 （必须要下一个最新版的谷歌浏览器哦）  
来自中国大陆的需搭配VPN使用  
**如何下载**:点击右侧的[release](https://github.com/Yudaotor/EsportsHelper/releases)下载
## 联系我
使用过程中有遇到什么问题或者建议可以在github上提出issue  
或者可以联系我  
telegram: https://t.me/Yudaotor  
discord: Khalil#7843  
可以给我点个小星星吗(*^_^*)⭐  
## 界面
![image](https://user-images.githubusercontent.com/87225219/228434642-6b7317e5-1c0a-4931-b358-f6e2b304429b.png)

## 运行平台  
windows,linux  

## 特性
1. 自动打开浏览器,进入lolesports.com,查询哪些赛区在进行比赛(在放录播的赛区会被忽视),进入观看并设置为最低清晰度(为了节省流量)
2. 可以自行设置是否选择无头模式(默认关闭)(无头模式即headless,开启后浏览器会不可见,在后台运行,缓解电脑CPU压力)
3. 可以自行设置不观看哪些赛区的比赛.(默认为空)(注意,此处是包含关系的逻辑,举例:当你设置了lck以后,lck_challengers同样不会观看)(建议设置,避免观看所有比赛从而被检测)
4. 可以自行设置多久来查询一次比赛最新信息.(默认600秒)(关闭已经结束的比赛和开启新开始的比赛)
5. 掉落提醒(支持钉钉,Discord,饭碗警告)(尚未测试,不确定是否生效)

## 配置信息
config.yaml
```yaml
### 必填项
username: "账号用户名"        # 必填，账号  
password: "密码"  # 必填，密码  
### 选填项
delay: 600                    # 每次检查的时间间隔，单位为秒(默认为600秒)(每次检测时间会在你设置的时延0.8-1.5倍之间随机波动)  
headless: False              # 设置为True时，程序会在后台运行，否则会打开浏览器窗口(默认为False)  
disWatchMatches: ["lck", "lpl", "lcs"] # 选填，不想看的赛区名称，可以在这里添加.(注意,是小写)  
runHours: -1                  # 负值为一直运行，正值为运行小时, 默认-1

connectorDropsUrl: "你的webhook链接"   # (支持钉钉,Discord,饭碗警告)(具体配置方法见此处[点我](https://github.com/Yudaotor/EsportsHelper/wiki/%E6%80%8E%E4%B9%88%E9%85%8D%E7%BD%AE%E6%8E%89%E8%90%BD%E6%8F%90%E9%86%92%3F(%E5%8A%9F%E8%83%BD%E5%BE%85%E6%B5%8B%E8%AF%95)))  
platForm: "windows"    # 使用平台,默认为windows,如需使用linux请在此处进行配置  
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
cblol:cblol  
cblol_academy:cblol_academy  
lla:lla  
ljl:ljl-japan  
ljl_academy:ljl_academy  
turkiye-sampiyonluk-ligi:turkiye-sampiyonluk-ligi  
cblol-brazil:cblol-brazil  
pcs:pcs  
honor_division:honor_division  
volcano_discover_league:volcano_discover_league  
hitpoint_masters:hitpoint_masters 
worlds:worlds  
european-masters:european-masters  
golden_league:movistar_fiber_golden_league  
honor_league:honor_league  
nlc:nlc  
elite_series:elite_series  
## by the way
本项目思路及部分代码来自Poro，感谢。[此处](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer)
