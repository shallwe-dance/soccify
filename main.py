"""
Naver Sports relay monitor — notifies on new away-team events.
Uses Chrome via Selenium (direct requests blocked by firewall).
Polls DOM every POLL_INTERVAL seconds.
"""
import time
import ctypes
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

GAME_ID = "l48mfcapdDIm7Wv"
PAGE_URL = f"https://m.sports.naver.com/game/{GAME_ID}/relay"
POLL_INTERVAL = 10  # seconds

def create_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--log-level=3")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)



def get_relay_items(driver) -> list[tuple[str, str, str]]:
    elements = driver.find_elements(By.CLASS_NAME, "TimeLine_relay_item__R67aM")
    result = []
    for el in elements:
        cls = el.get_attribute("class") or ""
        if "TimeLine_type_away__Nn8z5" in cls:
            team = "원정"
        elif "TimeLine_type_home__igEcj" in cls:
            team = "홈"
        else:
            continue
        data_no = el.get_attribute("data-no") or ""
        text = el.text.strip()
        if data_no:
            result.append((data_no, text, team))
    return result

def fetch_items(driver) -> list[tuple[str, str, str]]:
    driver.get(PAGE_URL)
    time.sleep(6)  # wait for SPA render + API calls
    return get_relay_items(driver)

def fetch_items(driver) -> list[tuple[str, str, str]]:
    driver.get(PAGE_URL)
    time.sleep(6)  # wait for SPA render + API calls
    return get_relay_items(driver)

def main() -> None:
    driver = create_driver()
    try:
        initial = fetch_items(driver)
        known: set[str] = {no for no, *_ in initial}
        print(f"초기 로드 완료: {len(known)}개 항목 (경기 전이면 0개 정상)")

        while True:
            time.sleep(POLL_INTERVAL)
            try:
                items = fetch_items(driver)
                new_items = [(no, text, team) for no, text, team in items if no not in known]
                for no, text, team in new_items:
                    notify(text, team)
                    known.add(no)
                if not new_items:
                    print("변경 없음")
            except Exception as e:
                print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
