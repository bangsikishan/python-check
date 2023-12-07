import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set Chrome options and service
chromedriver_path = "D:\\Python\\scrape\\chromedriver-win64\\chromedriver.exe"
service = Service(executable_path=chromedriver_path)

options = Options()
options.add_argument("--log-level=3")
# options.add_argument("--headless")

# Load website data
with open("test_websites_list.json", "r") as f:
    websites_list = json.load(f)

# Initialize WebDriver
driver = webdriver.Chrome(options=options, service=service)

wait = WebDriverWait(driver, 20)

def check_website(selector, selector_value, xpath):
    parent_element = wait.until(
        EC.visibility_of_element_located((selector, selector_value))
    )

    text = parent_element.find_element(By.XPATH, xpath).text

    return text
    

def get_selector(selector):
    match selector:
        case "classname":
            return By.CLASS_NAME
        case "id":
            return By.ID
        case "xpath":
            return By.XPATH
        case _:
            print("Invalid selector!")
            return None


results = {}
ecgains = []
for key, value in websites_list.items():
    try:
        driver.get(value["url"])
    except WebDriverException:
        print("Webdriver exception thrown!")

    try:
        text = check_website(
            get_selector(value["primary_selector"]),
            value["primary_selector_value"],
            value["primary_xpath"]
        )
    except NoSuchElementException:
        text = check_website(
            get_selector(value["secondary_selector"]),
            value["secondary_selector_value"],
            value["secondary_xpath"]
        )

    if text == value["message"]:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": False}
        ecgains.append(value["ecgain"])
    else:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": True}

driver.quit()

with open("results.json", "w") as f:
    json.dump(results, f, indent=4)

with open("ecgains.txt", "w") as f:
    ecgains_str = '","'.join(map(str, ecgains))
    f.write(f'"{ecgains_str}"')
