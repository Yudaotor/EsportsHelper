<p align="center">
<a href="https://github.com/Yudaotor/EsportsHelper"><img alt="EsportsHelper" src="https://i.328888.xyz/2023/03/28/itMRQF.png"></a><br/>
<a href="https://lolesports.com"><img alt="lolesports" src="https://img.shields.io/badge/WebSite-lol%20esports-445fa5.svg?style=plastic"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Yudaotor/EsportsHelper"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/pulls"><img alt="PRWelcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat"></a><br/>
<a href="https://www.cdnjson.com/images/2023/03/13/image-merge-1678713037835.png"><img alt="buymecoffee" src="https://user-images.githubusercontent.com/87225219/228188809-9d136e10-faa1-49b9-a6b7-b969dd1d8c7f.png"></a>
</p>

**Language**: [English](https://github.com/Yudaotor/EsportsHelper/blob/main/README.EN.md)|[Chinese](https://github.com/Yudaotor/EsportsHelper/blob/main/README.md)
# EsportsHelper
Automatically watch lolesports through selenium and undetected_chromedriver,url:[lolesports](lolesports.com)  
As for the question of whether it will be detected by riot, there is no answer yet.    
Oh, You must download Google Chrome (must be the next latest version)  
**HOW TO Download**:click here[release](https://github.com/Yudaotor/EsportsHelper/releases)

## GUI
![image](https://user-images.githubusercontent.com/87225219/228434642-6b7317e5-1c0a-4931-b358-f6e2b304429b.png)

## OS  
windows,linux  

### mac
Temporary operation method：
```shell
python -m pip install -r requirements.txt
./run_job.sh 0
```


## Feature
1. Automatically open your browser, go to lolesports.com, check which divisions are playing (the divisions that are playing recorded games will be ignored), enter to watch,turn on vol and set to the lowest stream. 
2. You can set whether to choose the headless mode (default off) (headless mode that is, headless, open the browser will not be visible, running in the background, to ease the pressure on the computer CPU)
3. You can set yourself which divisions you do not watch. (Default is empty) (Note, here is the logic of the inclusion relationship, for example: when you set lck, lck_challengers also will not watch) (recommended, to avoid watching all games and thus be detected)
4. You can set how often you want to check the latest information of the competition. (Default 600 seconds) (Close closed matches and open new ones)
5. Drop alert (Discord) (not yet tested, not sure if it works)
6. Error alerts can be sent when an error occurs in the software
7. You can set the maximum run time and close the software when the time is reached
8. You can set a hibernation time period in which the software will check at 1 hour intervals
9. You can set the desktop reminder (not yet tested, not sure if it works)
10. Add the function of adding proxy manually
11. You can open the function of deleting video elements (save net. risk unknown)

## Configuation
config.yaml
```yaml
### Required
username: "username"        # username  
password: "password"  # password  
### Optional
delay: 600                    # Time interval for each check in seconds (default is 600 seconds) (each detection time will fluctuate randomly between 0.8 and 1.5 times the time delay you set) 
headless: False              # When set to True, the program will run in the background, otherwise it will open a browser window (default is False)  
disWatchMatches: ["lck", "lpl", "lcs"] # Optional, you can add the name of the race you don't want to see here. (Note, it is lowercase)    
runHours: -1                  # negative value is always running, positive value is running hours, default -1
proxy: "" # proxy address, optional, not required for general users. e.g., "127.0.0.1:7890"
connectorDropsUrl: ""   # discord link
platForm: "windows"    # OS, the default is windows, if you want to use linux, please configure here  
closeStream: "False"   #  the function of deleting video elements (save net. risk unknown)
desktopNotify: "False"  # deskTopNotify
sleepPeriod: "8-13" # Hibernation time period, (default is empty) in the format of "start hour - end hour", will be checked in 1 hour intervals in the hibernation time period. The interval is left-closed and right-open.
```

## by the way
The project idea and part of the code are from Poro, thanks.[Here](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer)
