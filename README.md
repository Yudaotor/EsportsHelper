<p align="center">
<a href="https://github.com/Yudaotor/EsportsHelper"><img alt="EsportsHelper" src="https://i.328888.xyz/2023/03/28/itMRQF.png"></a><br/>
<a href="https://lolesports.com"><img alt="lolesports" src="https://img.shields.io/badge/WebSite-lol%20esports-445fa5.svg?style=plastic"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Yudaotor/EsportsHelper"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/pulls"><img alt="PRWelcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat"></a><br/>
<a href="https://www.cdnjson.com/images/2023/03/13/image-merge-1678713037835.png"><img alt="buymecoffee" src="https://user-images.githubusercontent.com/87225219/228188809-9d136e10-faa1-49b9-a6b7-b969dd1d8c7f.png"></a>
</p>

**Language**: [English](https://github.com/Yudaotor/EsportsHelper/blob/main/README.md) | [Chinese](https://github.com/Yudaotor/EsportsHelper/blob/main/README.CN.md)

# EsportsHelper
Automatically watch [LolEsports](lolesports.com) broadcasts using selenium and undetected_chromedriver.

Google Chrome must be downloaded in order to work (must be the latest version).

**DOWNLOAD**:

Click here: [Releases](https://github.com/Yudaotor/EsportsHelper/releases)

**WORD OF CAUTION:** 
To avoid detection by RIOT, please try to filter out the smaller league.  

## Contact Me
If you encounter any problems or suggestions in the process of use, feel free to create an issue on GitHub or contact me:

Telegram: https://t.me/Yudaotor, Discord username: Khalil#7843 

Can you please give me a little star?(*^_^*)⭐  

## GUI
![image](https://github.com/Yudaotor/EsportsHelper/assets/87225219/695f9b06-2283-4f98-9133-54e94f9ed81b)



## OS  
Windows, Linux  

## MacOS
Temporary operation method：
```shell
python -m pip install -r requirements.txt
./run_job.sh 0
```
## Multiple Account  
Unzip multiple folders, and then each different configuration files.Open all instances to achieve multiple account.

## Want Use Chromium on ARM64?
Read This!  -->[Guide](https://github.com/Yudaotor/EsportsHelper/wiki/The-Way-Using-Chromium-on-ARM64)
## Features
1. Automatically opens your browser, proceeds to lolesports.com, checks which leagues are currently playing (VODs will be ignored), enters to watch, turns on the volume and sets the quality of the stream to the lowest. 
2. Option to set whether program will launch in headless mode or with a visible browser window (Off by default). Headless mode is opening the browser without GUI. (It will not be visible, set to running in the background in order to lower CPU usage).
3. Option to set **which Leagues broadcasts to ignore**. (Empty by default). Please note, that there is a logic of the inclusion relationship, for example: if LCK is set to be ignored, LCK_Challengers will also be ignored. (This option is highly recommended, avoid watching all broadcasts and be detected because of that).
4. Option to set how often the latest information about the broadcast will be checked. (600 seconds by default). Upon checking, it will close ended broadcasts and open new ones.
5. **Drop alerts** using Discord webhook.
6. Error alerts when an error occurs in the software.
7. Option to set the maximum run time of program. It will force PC shutdown when the time limit is reached.(only windows will do shutdown)
8. Option to set multiple hibernation period in which the software will close lolesports site,waiting until the end if period and reopen.
9. Desktop notifications. 
10. Option to manually add a proxy.
11. Option of **deleting video-player elements** in order to save traffic. (Risk known).
12. You can view the number of drops and the drop information of current session.
13. Password-free login using local browser cookies.
14. You can customize the path of Google Chrome installation (Portable version).
15. Both **Simplified Chinese**, **Traditional Chinese** and **English** are supported
16. **Auto sleep mode**, which will close all webpages related to Lolesports when there are no ongoing matches, achieving a true non-24/7.(This option is highly recommended)
17. You can set a **maximum number of simultaneous streams** to avoid being detected by RIOT for watching too many steams at the same time.
18. You can export total drop details file.
19. **Safe mode** can be switched on to automatically filter out small leagues.
## Configuation
Using config.yaml file.
```yaml

## Required fields in config.yaml
Username: "username"  # Riot account username  
Password: "password"  # Riot account password  

## Optional

delay: 600                              # Time interval for each check in seconds (600 seconds by default). Each check time will fluctuate randomly between 0.8 and 1.5 times the time delay you set. 
headless: False                         # When set to True, the program will run in the background; otherwise it will open a browser window (False by default).  
nickName: ""                            # nickName, default is username.
mode: "safe"                            # Mode selection, safe for safe mode, narmal for narmal mode, default is safe. For details, see github
# 更多配置请参考readme中的配置说明 / Refer to the Readme file for more configuration options.
briefLogLength: 10                      # Length of log brief information. Default is 10.
onlyWatchMatches: ["lcs","lla","lpl","lck","ljl-japan","lco","lec","cblol-brazil","pcs","tft_esports"] 
disWatchMatches: []                     # Optional, here you can add Leagues you wish to ignore. Please note, names should be in lowercase.    
language: "en_US"                       # en_US for English.zh_CN for Simplified Chinese,zh_TW for Traditional Chinese.
maxStream: 3                            # The default value is 3, which is the maximum number of matches that can be watched at the same time, beyond which they will not be watched.
maxRunHours: -1                         # Negative value is always running, positive value is running by hours, default -1.
proxy: ""                               # Proxy address, not required for general users, e.g., "127.0.0.1:7890".
connectorDropsUrl: ""                   # Discord webhook link.
exportDrops: False                      # Default is False, whether or not you need to export the total drop details file, it will only be generated when the script is opened.
platForm: "windows"                     # OS, Windows is set by default. If you want to use the program on Linux, please change the value here.  
closeStream: False                      # Option of deleting video-player elements to save traffic. (Risk).
desktopNotify: False                    # Experimental feature to enable Desktop notifications.
sleepPeriod: ["8-13", "20-23"]          # Hibernation period, empty by default, allowed multiple period. The format is "Start hour – End hour". Tabs will be closed and reopened at the end of sleep.
ignoreBroadCast: True                   # Option to ignore broadcasts.
userDataDir: "C:\\Users\\xxxxx\\AppData\\Local\\Google\\Chrome\\User Data"  # Path to Chrome cookie files. 
chromePath: "X:\\xxxxx\\xx\\Chrome.exe" # Chrome.exe location.
countDrops: True                        # Option to monitor Drops number.
autoSleep: True                         # which will close all webpages related to Lolesports when there are no ongoing matches, achieving a true non-24/7.

```

## Honorable mention
The project idea and part of the code are from Poro, kudos. [Here is the link to the original Farmer](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer).
