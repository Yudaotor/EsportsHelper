FROM ghcr.io/linuxserver/baseimage-kasmvnc:alpine318

LABEL build_version="1.3.1"
LABEL maintainer="Pablo Duval <pablo@redroot.me>"

# Install necessary dependencies
RUN \
  echo "**** Installing dependencies ****" && \
  apk add --no-cache \
    chromium \
    ffmpeg \
    chromium-chromedriver \
    py3-pip \
    git && \
  echo "**** Cleaning up ****" && \
  rm -rf /tmp/*

# Create the /defaults directory
RUN mkdir -p /defaults

# Create autostart script
RUN echo '#!/bin/bash' > /defaults/autostart
RUN echo 'cd /esportshelper && python3 main.py' >> /defaults/autostart
RUN chmod +x /defaults/autostart

# Create a restart script
RUN echo '#!/bin/bash' > /defaults/restart_esportshelper.sh
RUN echo 'pkill -f "python3 main.py"' >> /defaults/restart_esportshelper.sh
RUN echo 'cd /esportshelper && python3 main.py' >> /defaults/restart_esportshelper.sh
RUN chmod +x /defaults/restart_esportshelper.sh

# Create menu.xml
RUN echo '<?xml version="1.0" encoding="utf-8"?>' > /defaults/menu.xml
RUN echo '<openbox_menu xmlns="http://openbox.org/3.4/menu">' >> /defaults/menu.xml
RUN echo '  <menu id="root-menu" label="MENU">' >> /defaults/menu.xml
RUN echo '    <item label="Terminal" icon="/usr/share/pixmaps/xterm-color_48x48.xpm"><action name="Execute"><command>/usr/bin/xterm</command></action></item>' >> /defaults/menu.xml
RUN echo '    <item label="Restart EsportsHelper" icon="/usr/share/pixmaps/xterm-color_48x48.xpm"><action name="Execute"><command>/defaults/restart_esportshelper.sh/command></action></item>' >> /defaults/menu.xml
RUN echo '    <item label="Chromium" icon="/usr/share/icons/hicolor/48x48/apps/chromium.png"><action name="Execute"><command>/usr/bin/chromium-browser</command></action></item>' >> /defaults/menu.xml
RUN echo '  </menu>' >> /defaults/menu.xml
RUN echo '</openbox_menu>' >> /defaults/menu.xml

# Prepare undetected_chromedriver
RUN mkdir -p /undetected_chromedriver && \
    cp /usr/bin/chromedriver /undetected_chromedriver/chromedriver && \
    chmod -R 777 /undetected_chromedriver

# Clone the EsportsHelper repository
RUN mkdir -p /esportshelper && \
    git clone https://github.com/Yudaotor/EsportsHelper /esportshelper && \
    chmod -R 777 /esportshelper

# Set permissions for chromium
RUN chmod -R 777 /usr/bin/chromium

# Set the working directory
WORKDIR /esportshelper

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 3000
EXPOSE 3000

# Remove git package
RUN apk del git

# Define a volume for /config
VOLUME /config
