<p align="center">
<a href="https://github.com/Yudaotor/EsportsHelper"><img alt="EsportsHelper" src="https://github.com/Yudaotor/EsportsHelper/assets/87225219/79896860-f119-4e69-bac7-148504d4c2ae"></a><br/>
<a href="https://lolesports.com"><img alt="lolesports" src="https://img.shields.io/badge/WebSite-lol%20esports-445fa5.svg?style=plastic"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Yudaotor/EsportsHelper"></a>
<a href="https://github.com/Yudaotor/EsportsHelper/pulls"><img alt="PRWelcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat"></a><br/>
<a href="https://www.cdnjson.com/images/2023/03/13/image-merge-1678713037835.png">点它-><img alt="buymecoffee" src="https://user-images.githubusercontent.com/87225219/228188809-9d136e10-faa1-49b9-a6b7-b969dd1d8c7f.png"></a>
</p>

**Language**: [English](https://github.com/Yudaotor/EsportsHelper/blob/main/README.EN.md) | [Chinese](https://github.com/Yudaotor/EsportsHelper/blob/main/README.md) | [Spanish](https://github.com/Yudaotor/EsportsHelper/blob/main/README.ES.md)

# EsportsHelper
Visualiza automáticamente las transmisiones de [LolEsports](lolesports.com) utilizando Selenium y undetected_chromedriver.

Google Chrome debe estar descargado para que funcione (debe ser la última versión).

**DESCARGA**:

Haz clic aquí: [Versiones](https://github.com/Yudaotor/EsportsHelper/releases)

**PALABRAS DE PRECAUCIÓN:** 
Para evitar ser detectado por RIOT, intenta filtrar las ligas más pequeñas (modo: "seguro" está bien). **¡No veas más de 5 partidas al mismo tiempo!**   

## Contáctame
Si encuentras algún problema o tienes sugerencias durante el uso, no dudes en crear un problema en GitHub o contactarme:

Telegram: **https://t.me/Yudaotor**, Nombre de usuario en Discord: **Khalil#7843** 

¿Me darías una pequeña estrella? (*^_^*)⭐  

## GUI
![imagen](https://i.imgur.com/eTKmeav.png)



## Sistemas operativos  
Windows, Linux  

## MacOS
Método de operación temporal：
```shell
python -m pip install -r requirements.txt
./run_job.sh 0
```
## Cuentas Múltiples 
Descomprime varias carpetas y luego archivos de configuración diferentes. Abre todas las instancias para utilizar múltiples cuentas. Si esto no es de tu agrado también puedes utilizar nuestra imagen de Docker.

## Versión Dockerizada
Para utilizar nuestra versión (no oficial) de Docker puedes utilizar nuestro "docker-compose.yml", simplemente colócalo en la ubicación que desees junto con el archivo de configuración "config.yaml" (puedes utilizar nuestra herramienta web) y ejecuta "sudo docker compose up -d". No olvides que la variable "isDockerized" debe estar en "True" en el archivo de configuración.
Ten en cuenta que esta aplicación utiliza un navegador real (Chromium/Chrome) lo que implica que pueda consumir hasta 2 GB de memoria ram.

## Features
1. Abre automáticamente tu navegador, va a lolesports.com, verifica qué ligas están jugando actualmente (ignora los VOD), entra a ver, enciende el volumen y ajusta la calidad de la transmisión al mínimo.
2. Opción para definir si el programa se lanzará en modo sin cabeza o con una ventana de navegador visible (desactivado por defecto). El modo sin cabeza abre el navegador sin GUI (no será visible, configurado para ejecutarse en segundo plano para reducir el uso de la CPU).
3. Opción para definir qué ligas de deportes electrónicos ignorar. (Vacío por defecto). Toma en cuenta que hay una lógica de relación de inclusión; por ejemplo: si LCK se configura para ser ignorada, LCK_Challengers también será ignorada. (Esta opción es muy recomendable, evita ver todas las transmisiones y ser detectado por ello).
4. Opción para configurar con qué frecuencia se verificará la información más reciente sobre la transmisión. (600 segundos por defecto). Al verificar, cerrará las transmisiones que hayan terminado y abrirá nuevas.
5. **Alertas de drops** utilizando webhook de Discord.
6. Alertas de error cuando ocurra un error en el software.
7. Opción para establecer el tiempo máximo de ejecución del programa. Forzará el apagado de la PC cuando se alcance el límite de tiempo (solo en Windows).
8. Opción para establecer varios períodos de hibernación en los que el software cerrará el sitio de lolesports, esperará hasta el final del período y lo reabrirá.
9. Notificaciones en el escritorio.
10. Opción para agregar manualmente un proxy.
11. Opción de **eliminar elementos del reproductor de video** para ahorrar tráfico. (Riesgo conocido).
12. Puedes ver el número de drops y la información de los drops de la sesión actual.
13. Inicio de sesión sin contraseña utilizando cookies del navegador local.
14. Puedes personalizar la ruta de instalación de Google Chrome (versión portátil).
15. Soporta **Chino Simplificado**, **Chino Tradicional**, **Inglés** y **Español**.
16. **Modo de suspensión automático**, que cerrará todas las páginas web relacionadas con Lolesports cuando no haya partidos en curso, logrando un verdadero no 24/7. (Esta opción es muy recomendable).
17. Puedes establecer un **número máximo de transmisiones simultáneas** para evitar ser detectado por RIOT por ver demasiadas transmisiones al mismo tiempo.
18. Puedes exportar el archivo de detalles de los drops totales.
19. El **Modo Seguro** se puede activar para filtrar automáticamente las ligas pequeñas.

    
## Configuración
Usando el archivo config.yaml.
```yaml

## Campos obligatorios en config.yaml
Username: "nombre_de_usuario"  # Nombre de usuario de la cuenta de Riot  
Password: "contraseña"  # Contraseña de la cuenta de Riot  

## Opcionales

delay: 600                              # Intervalo de tiempo para cada comprobación en segundos (600 segundos por defecto). Cada tiempo de comprobación fluctuará aleatoriamente entre 0.8 y 1.5 veces el retraso que establezcas. 
headless: False                         # Cuando se establezca en True, el programa se ejecutará en segundo plano; de lo contrario, abrirá una ventana de navegador (False por defecto).  
nickName: ""                            # Apodo para la cuenta añadida, por defecto "nombre_de_usuario".
mode: "seguro"                            # Selección de modo: "seguro" para el modo seguro, "normal" para el modo normal, por defecto es "seguro". Consulta la página de GitHub para más detalles.
# Más opciones de configuración en el archivo README / Please refer to the Readme file for more configuration options
briefLogLength: 10                      # Longitud del resumen de información del registro. Por defecto es 10.
onlyWatchMatches: ["lcs","lla","lpl","lck","ljl-japan","lco","lec","cblol-brazil","pcs","tft_esports"] 
disWatchMatches: []                     # Opcional, aquí puedes añadir las ligas que deseas ignorar. Ten en cuenta que los nombres deben estar en minúsculas.    
language: "es_ES"                       # en_US para inglés, es_ES para chino simplificado, zh_TW para chino tradicional.
maxStream: 4                            # El valor por defecto es 4, que es el número máximo de partidas que se pueden ver al mismo tiempo, más allá de ese número no se verán.
maxRunHours: -1                         # Un valor negativo es que siempre estará en ejecución, un valor positivo será en horas, por defecto es -1.
proxy: ""                               # Dirección del proxy, no es necesario para usuarios generales, por ejemplo, "127.0.0.1:7890".
connectorDropsUrl: ""                   # Enlace del webhook de Discord.
exportDrops: False                      # Por defecto es False, si necesitas o no exportar el archivo con detalles totales de caídas, solo se generará cuando el script esté abierto.
platForm: "windows"                     # Sistema operativo, por defecto es Windows. Si quieres usar el programa en Linux, cambia el valor aquí.  
arm64: False                            # Habilita la compatibilidad para utilizar Chromium en Linux ARM64, se requiere platForm: "linux" y tener el chromedriver en "/home/USERNAME/.local/share/undetected_chromedriver/chromedriver", más información: https://github.com/Yudaotor/EsportsHelper/wiki/The-Way-Using-Chromium-on-ARM64
closeStream: False                      # Opción para eliminar elementos del reproductor de video para ahorrar tráfico. (Riesgo).
desktopNotify: False                    # Función experimental para habilitar notificaciones de escritorio.
sleepPeriod: ["8-13", "20-23"]          # Período de hibernación, vacío por defecto, se permiten varios períodos. El formato es "Hora de inicio – Hora de fin". Las pestañas se cerrarán y se volverán a abrir al final del período de hibernación.
ignoreBroadCast: True                   # Opción para ignorar transmisiones.
userDataDir: "C:\\Users\\xxxxx\\AppData\\Local\\Google\\Chrome\\User Data"  # Ruta de los archivos de cookies de Chrome. 
chromePath: "X:\\xxxxx\\xx\\Chrome.exe" # Ubicación de Chrome.exe.
countDrops: True                        # Opción para controlar el número de caídas.
autoSleep: True                         # Activar o desactivar el modo de sueño automático: dormir cuando no haya partidas en vivo, despertar cuando comiencen las partidas (True por defecto).
debug: False                            # Modo de depuración, por defecto es False.
isDockerized: False                     # Solo se debe activar si la EsportsHelper está siendo ejecutado en un contenedor de Docker.
```

## Mención especial
La idea del proyecto y parte del código provienen de Poro, un agradecimiento a él. [Aquí está el enlace al Farmer original](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer).
