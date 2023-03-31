<p align="center">
<a href="https://github.com/Yudaotor/EsportsHelper"><img alt="EsportsHelper" src="https://i.328888.xyz/2023/03/28/itMRQF.png"></a><br/>
<a href="https://lolesports.com"><img alt="lolesports" src="https://img.shields.io/badge/WebSite-lol%20esports-445fa5.svg?style=plastic"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Yudaotor/EsportsHelper"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/pulls"><img alt="PRWelcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat"></a><br/>
<a href="https://www.cdnjson.com/images/2023/03/13/image-merge-1678713037835.png"><img alt="buymecoffee" src="https://user-images.githubusercontent.com/87225219/228188809-9d136e10-faa1-49b9-a6b7-b969dd1d8c7f.png"></a>
</p>


# EsportsHelper
Automatically watch lolesports through selenium and undetected_chromedriver,url:[lolesports](lolesports.com)  
As for the question of whether it will be detected by riot, there is no answer yet.    
Oh, You must download Google Chrome (must be the next latest version)  
**HOW TO Download**:click here[release](https://github.com/Yudaotor/EsportsHelper/releases)
## Contact Me
If you encounter any problems or suggestions in the process of use, you can create an issue on github  
Or you can contact me by
telegram: https://t.me/Yudaotor  
discord: Khalil#7843  
Can you give me a little star?(*^_^*)⭐  
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
runHours: -1                  # (not yet implemented) negative value is always running, positive value is running hours, default -1
proxy: "" # (Not yet implemented) proxy address, optional, not required for general users. e.g., "socks://127.0.0.1:20173"
connectorDropsUrl: ""   # discord link
platForm: "windows"    # OS, the default is windows, if you want to use linux, please configure here  
```

## by the way
The project idea and part of the code are from Poro, thanks.[Here](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer)
