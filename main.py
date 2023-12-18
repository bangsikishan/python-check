import json
from typing import Optional
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
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--log-level=3")
options.add_argument("--headless")


# Load website data
with open("test_websites_list.json", "r") as f:
    websites_list = json.load(f)

# Initialize WebDriver
driver = webdriver.Chrome(options=options, service=service)

wait = WebDriverWait(driver, 30)

def get_element_text(selector: By, selector_value: str, xpath: str) -> str:
    try:
        parent_element = wait.until(
            EC.visibility_of_element_located((selector, selector_value))
        )
    
        return parent_element.find_element(By.XPATH, xpath).text
    except (NoSuchElementException, TimeoutException):
        return ""
    
def get_text_from_selector(selectors: dict) -> str:
    primary_text = get_element_text(
        get_selector(selectors["primary_selector"]),
        selectors["primary_selector_value"],
        selectors["primary_xpath"]
    )

    if primary_text:
        return primary_text
    
    return get_element_text(
        get_selector(selectors["secondary_selector"]),
        selectors["secondary_selector_value"],
        selectors["secondary_xpath"]
    )


def get_selector(selector: str) -> Optional[By]:
    return {
        "classname": By.CLASS_NAME,
        "id": By.ID,
        "xpath": By.XPATH
    }.get(selector, None) or print("Invalid selector!")


results = {}
ecgains = []
for key, value in websites_list.items():
    print(f"[+] Trying website {key} out of {len(websites_list)}...", end="\r")

    try:
        driver.get(value["url"])
    except WebDriverException:
        print("Webdriver exception thrown!")

    text = get_text_from_selector(value)

    if text == value["message"]:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": False}
        ecgains.append(value["ecgain"])
    else:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": True}
        value["message"] = text.replace("\n", "\n")
print("")
driver.quit()

with open("test_websites_list.json", "w") as f:
    json.dump(websites_list, f, indent=4)

with open("results.json", "w") as f:
    json.dump(results, f, indent=4)

with open("ecgains.txt", "w") as f:
    ecgains_str = '","'.join(map(str, ecgains))
    f.write(f'"{ecgains_str}"')
