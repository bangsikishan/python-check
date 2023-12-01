import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chromedriver_path = "D:\\Python\\scrape\\chromedriver-win64\\chromedriver.exe"
service = Service(executable_path=chromedriver_path)

options = Options()
options.add_argument("--log-level=3")
options.add_argument("--headless")

with open("websites_list.json", "r") as f:
    websites_list = json.load(f)

driver = webdriver.Chrome(options=options, service=service)

results = {}
messages = {}
ecgains = []
for key, value in websites_list.items():
    print(f"[+] Checking website {key} out of {len(websites_list)}...", end="\r")

    driver.get(value["url"])
    # with open("source1.html", "w", encoding="utf-8") as f:
    #     f.write(driver.page_source)
    time.sleep(2)

    try:
        text = driver.find_element(By.XPATH, value["xpath"]).text
    except Exception as e:
        # print(e)
        results[key] = {"ecgain": value["ecgain"], "contains_bids": "Exception thrown! Check Manually."}
        continue
    
    if value["message"] == text:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": False}
        ecgains.append(value["ecgain"])
    else:
        results[key] = {"ecgain": value["ecgain"], "contains_bids": True}
        # messages[key] = {"ecgain": value["ecgain"], "message": text.replace("\n", "\n")}
        messages[key] = {"ecgain": value["ecgain"], "url": value["url"], "xpath": value["xpath"], "message": text.replace("\n", "\n")}
print("")

driver.quit()

new_websites_list = {**websites_list, **messages}

with open("results.json", "w") as f:
    json.dump(results, f)

with open("test_websites_list.json", "w") as f:
    json.dump(new_websites_list, f)

# with open("messages.json", "w") as f:
#     json.dump(messages, f)

result = '","'.join(map(str, ecgains))
result = f'"{result}"'
with open("ecgains.txt", "w") as f:
    f.write(result)
