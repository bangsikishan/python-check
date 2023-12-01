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
options.add_argument("--headless")

# Load website data
with open("websites_list.json", "r") as f:
    websites_list = json.load(f)

# Initialize WebDriver
driver = webdriver.Chrome(options=options, service=service)

# List to store ecgains
ecgains = []

# Dictionary to store results
results = {}

# Loop through websites
for key, value in websites_list.items():
    print(f"[+] Checking website {key} out of {len(websites_list)}...", end="\r")

    try:
        driver.get(value["url"])
    except WebDriverException:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": f"Exception thrown! Could not resolve {value['url']}"}
        continue

    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, value["xpath"]))
        )

        text = element.text if element else None
        
        if text == value["message"]:
            contains_bids = False
            ecgains.append(value["ecgain"])
        else:
            contains_bids = True
            websites_list[key]["message"] = text.replace("\n", "\n")

        results[key] = {"ecgain": value["ecgain"], "contains_bids": contains_bids}
    except NoSuchElementException:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": "Exception thrown! Check Manually."}
    except TimeoutException:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": "Exception thrown! Check Manually."}
print("")

# Quit WebDriver
driver.quit()

# Save results to JSON
with open("results.json", "w") as f:
    json.dump(results, f, indent=4)

# Write new data to JSON
with open("test_websites_list.json", "w") as f:
    json.dump(websites_list, f, indent=4)

# Write ecgains to a text file
with open("ecgains.txt", "w") as f:
    ecgains_str = '","'.join(map(str, ecgains))
    f.write(f'"{ecgains_str}"')
