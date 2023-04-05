import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

email = os.environ.get("RMM_Email")
password = os.environ.get("RMM_PASSWORD")

file_name = "test.txt"
with open(file_name, "w") as f:
    f.write("This is a test file")

# Set up the mobile browser user agent
mobile_emulation = {
    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
}

chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

# Set up the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the website and find the login button
driver.get("https://redmountainmakers.org/")
login_button = driver.find_element(By.CSS_SELECTOR, '.mobilePanelButton.buttonLogin')

# Click the login button to reveal the login form
login_button.click()

# Find the username and password fields and fill them in
username_field = driver.find_element(By.ID, "id_QFpB82d_userName")
password_field = driver.find_element(By.ID, "id_QFpB82d_password")
username_field.send_keys(email)
password_field.send_keys(password)

submit_button = driver.find_element(By.ID, "id_QFpB82d_loginAction")
submit_button.click()

admin_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.-wa-admin-switcher_admin-view-link')))
admin_button.click()

website_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.-wa-menu-icon[title="Website"]')))
website_button.click()

files_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Files")))
files_button.click()

# Switch to the iframe containing the file browser
iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "idcms_resourceManagement_browser_Frame")))
driver.switch_to.frame(iframe)

expand_files = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ygtvt1 > .ygtvspacer')))
try:
    expand_files.click()
except StaleElementReferenceException:
    # Retry clicking the element if it becomes stale
    expand_files = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#ygtvt1 > .ygtvspacer')))
    expand_files.click()

event_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ygtvlabelel5")))
event_button.click()

upload_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.iconUpload')))
upload_button.click()

file_path = Path(file_name).resolve()

file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "file")))
file_input.send_keys(file_path)

ok_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,"ithit_interface_uploadResource_subm_label")))
ok_button.click()


driver.quit()
