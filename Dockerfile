FROM alpine:latest

LABEL maintainer="Pablo Duval <pablo@redroot.me>"

ENV NOVNC_PASSWORD=esportshelper

RUN apk add --no-cache sudo git xfce4 faenza-icon-theme bash python3 py3-pip tigervnc xfce4-terminal chromium ffmpeg chromium-chromedriver cmake wget \
    pulseaudio xfce4-pulseaudio-plugin pavucontrol pulseaudio-alsa alsa-plugins-pulse alsa-lib-dev nodejs npm gcc build-base libffi-dev yaml-dev mousepad \
    build-base \
    && adduser -h /home/alpine -s /bin/bash -S -D alpine && echo -e "alpine\nalpine" | passwd alpine \
    && echo 'alpine ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && git clone https://github.com/novnc/noVNC /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify \
    && rm -f \
        /etc/xdg/autostart/xfce4-power-manager.desktop \
        /etc/xdg/autostart/xscreensaver.desktop \
        /usr/share/xfce4/panel/plugins/power-manager-plugin.desktop

COPY docker-novnc/script.js /opt/noVNC/script.js
COPY docker-novnc/audify.js /opt/noVNC/audify.js
COPY docker-novnc/vnc.html /opt/noVNC/vnc.html
COPY docker-novnc/pcm-player.js /opt/noVNC/pcm-player.js

RUN npm install --prefix /opt/noVNC ws
RUN npm install --prefix /opt/noVNC audify

USER alpine
WORKDIR /home/alpine

RUN mkdir -p /home/alpine/.vnc \
    && echo -e "-Securitytypes=VNCAuth" > /home/alpine/.vnc/config \
    && echo -e "#!/bin/bash\nstartxfce4 &" > /home/alpine/.vnc/xstartup \
    && echo -e "$NOVNC_PASSWORD\n$NOVNC_PASSWORD\nn\n" | vncpasswd

USER root

RUN echo '\
#!/bin/bash \
/usr/bin/vncserver :99 2>&1 | sed  "s/^/[Xtigervnc ] /" & \
sleep 1 & \
/usr/bin/pulseaudio 2>&1 | sed  "s/^/[pulseaudio] /" & \
sleep 1 & \
/usr/bin/node /opt/noVNC/audify.js 2>&1 | sed "s/^/[audify    ] /" & \
/opt/noVNC/utils/novnc_proxy --vnc localhost:5999 2>&1 | sed "s/^/[noVNC     ] /"'\
>/entry.sh

RUN rm -rf /usr/bin/gnome-keyring*

USER alpine

# Crea el directorio si no existe, luego clona el repositorio
RUN mkdir -p /home/alpine/Desktop/EsportsHelper && \
    git clone https://github.com/redr00t/EsportsHelper.git /home/alpine/Desktop/EsportsHelper

# Instala los paquetes pip desde el archivo requirements.txt
RUN pip install --no-cache-dir -r /home/alpine/Desktop/EsportsHelper/requirements.txt

# Mueve el archivo config.yaml al directorio deseado después de clonar el repositorio
COPY docker-novnc/config.yaml /home/alpine/Desktop/EsportsHelper/config.yaml

RUN mkdir -p /home/alpine/.local/share/undetected_chromedriver \
    && cp /usr/bin/chromedriver /home/alpine/.local/share/undetected_chromedriver/chromedriver

ENTRYPOINT [ "/bin/bash", "/entry.sh" ]