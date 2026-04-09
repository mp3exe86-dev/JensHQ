from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service("C:/JobAgent/shared/drivers/chromedriver.exe")

driver = webdriver.Chrome(service=service)

driver.get("https://google.com")

input("Press Enter to close...")
driver.quit()