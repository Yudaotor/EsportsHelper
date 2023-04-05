import random
import time
import requests

from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Define variables
url = "https://lolesports.com/"
username = 'your_username'
password = "your_riot_account_password"
num_streams = 3

# Define display
#display = Display(visible=0, size=(1920, 1080))
#display.start()

url = 'https://lolesports.com/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Set Chrome options to run headless and mimic user agent
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')

# Launch Chrome browser
driver = webdriver.Chrome(options=chrome_options)

# Login to Riot account
driver.get(url)
wait = WebDriverWait(driver, 10)
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="login-submit-button"]')))
login_button = wait.until(EC.presence_of_element_located(
    (By.CLASS_NAME, 'auth0-lock-submit')))
login_button.click()
email_field = driver.find_element_by_name('username')
email_field.send_keys(username)
password_field = driver.find_element_by_name('password')
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)

# Choose the three most viewed streams
driver.get(url + 'watch')
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'stream-tile')))
streams = driver.find_elements_by_class_name('stream-tile')
viewers = {}
for stream in streams:
    viewers[stream] = int(stream.find_element_by_class_name(
        'viewer-count').text.split()[0])
top_streams = [stream for stream, views in sorted(
    viewers.items(), key=lambda x: x[1], reverse=True)[:num_streams]]
print(top_streams)

# Watch each stream in the virtual browser
for stream in top_streams:
    stream_url = stream.find_element_by_tag_name('a').get_attribute('href')
    driver.execute_script("window.open('{}', '_blank');".format(stream_url))
    time.sleep(random.uniform(5, 10))

# Close virtual display and browser
#display.stop()
#driver.quit()
