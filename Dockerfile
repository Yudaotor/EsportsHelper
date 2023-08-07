# We use the Python Alpine base image
FROM python:alpine

# We install the necessary dependencies
RUN apk update && \
    apk add --no-cache gcc ffmpeg chromium chromium-chromedriver ca-certificates \
                        build-base libffi-dev yaml-dev && \
    rm -rf /var/cache/apk/*

# We install Cython and virtualenv
RUN pip install cython virtualenv

# We set the working directory
WORKDIR /app

# We copy the entire current directory to the container
COPY . /app

# We create a virtual environment using virtualenv and activate it
RUN virtualenv venv
ENV PATH="/app/venv/bin:$PATH"

# We install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3","./main.py"]
