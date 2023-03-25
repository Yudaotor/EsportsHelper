# EsportsHelper
通过selenium模拟浏览器来自动观看电竞比赛,网址:[lolesports](lolesports.com)  
至于会不会被拳头检测到这个问题,目前还没有答案.
**如何下载**:点击右侧的[release](https://github.com/Yudaotor/EsportsHelper/releases)下载
## 联系我
使用过程中有遇到什么问题在github上提出issue  
或者可以联系我  
telegram: https://t.me/Yudaotor  
discord: Khalil#7843  
可以给我点个小星星吗(*^_^*)⭐  
## 界面
![image](https://user-images.githubusercontent.com/87225219/227703640-4ddeb386-36c8-4940-87bd-8af654d377a8.png)


## 特性
1. 自动打开浏览器,进入lolesports.com,查询哪些赛区在进行比赛(在放录播的赛区会被忽视),进入观看并设置为最低清晰度(为了节省流量)
2. 可以自行设置是否选择无头模式(默认关闭)(无头模式即headless,开启后浏览器会不可见,在后台运行,缓解电脑CPU压力)
3. 可以自行设置不观看哪些赛区的比赛.(默认为空)(注意,此处是包含关系的逻辑,举例:当你设置了lck以后,lck_challengers同样不会观看)
4. 可以自行设置多久来查询一次比赛最新信息.(默认600秒)(关闭已经结束的比赛和开启新开始的比赛)

## 配置信息

delay: 600                    # 每次检查的时间间隔，单位为秒(默认为600秒)  
headless: False              # 设置为True时，程序会在后台运行，否则会打开浏览器窗口(默认为False)  
username: "账号用户名"        # 必填，账号  
password: "密码"  # 必填，密码  
disWatchMatches: ["lck", "lpl", "lcs"] # 选填，不想看的赛区名称，可以在这里添加.(注意,是小写)  
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
