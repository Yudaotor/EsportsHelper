# We define the base image
FROM debian:bookworm

# We update and install necessary dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y ffmpeg chromium python3 python3-pip python3-venv

# We set the working directory
WORKDIR /app

# We copy the entire current directory to the container
COPY . /app

# We create a virtual environment and activate it
RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# We install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# We run the Python bot
CMD [ "python3", "./main.py" ]
