# get_cookies_ptit_lms_fix.py
# Python 3.10+ | pip install -U selenium

# Refactored as a class
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

class LMSCookieFetcher:
    START_URL = "https://lms.ptit.edu.vn/"
    LMS_COOKIE_NAME = "session_id"
    WAIT_SHORT = 6
    WAIT_STD = 30
    WAIT_LONG = 50

    def __init__(self, email, password, headless=True):
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None

    def detect_chrome_binary(self):
        for p in [
            os.getenv("CHROME_BINARY"),
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]:
            if p and os.path.exists(p):
                return p
        for name in ["google-chrome-stable", "google-chrome", "chromium", "chromium-browser", "chrome"]:
            p = shutil.which(name)
            if p:
                return p
        return None

    def ensure_latest_window(self):
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
        except Exception:
            pass

    def safe_click(self, locator, timeout=None, attempts=4, js_fallback=True):
        if timeout is None:
            timeout = self.WAIT_STD
        last_err = None
        for i in range(attempts):
            try:
                el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
                el.click()
                return el
            except (StaleElementReferenceException, ElementClickInterceptedException) as e:
                last_err = e
                time.sleep(0.6)
                continue
        if js_fallback:
            el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            self.driver.execute_script("arguments[0].click();", el)
            return el
        if last_err:
            raise last_err

    def wait_sendkeys(self, locator, text, timeout=None, clear_first=True, press_enter=False):
        if timeout is None:
            timeout = self.WAIT_STD
        el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        try:
            if clear_first:
                el.clear()
        except Exception:
            pass
        el.send_keys(text + (Keys.ENTER if press_enter else ""))
        return el

    def get_cookie_when_ready(self, name, url_substr="lms.ptit.edu.vn", timeout=None):
        if timeout is None:
            timeout = self.WAIT_LONG
        end = time.time() + timeout
        while time.time() < end:
            try:
                if url_substr in (self.driver.current_url or ""):
                    ck = self.driver.get_cookie(name)
                    if ck and ck.get("value"):
                        return ck
            except Exception:
                pass
            time.sleep(1)
        return None

    def element_exists(self, locator, timeout=None):
        if timeout is None:
            timeout = self.WAIT_SHORT
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def fetch_cookie(self):
        chrome_bin = self.detect_chrome_binary()
        if not chrome_bin:
            raise RuntimeError("Không tìm thấy Chrome/Chromium. Cài 'chromium' hoặc đặt CHROME_BINARY.")
        opts = Options()
        opts.binary_location = chrome_bin
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        if self.headless:
            opts.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=opts)
        wait = WebDriverWait(self.driver, self.WAIT_STD)

        try:
            print(f"[1] Mở {self.START_URL}")
            self.driver.get(self.START_URL)

            print("[2] Bấm 'Đăng nhập'")
            try:
                self.safe_click((By.CSS_SELECTOR, "a.btn-login"))
            except TimeoutException:
                self.safe_click((By.CSS_SELECTOR, 'a[href="/web/login"]'))

            self.ensure_latest_window()

            print("[3] Chọn 'Đăng nhập bằng SLink ID' và nhập thông tin")
            try:
                self.safe_click((By.PARTIAL_LINK_TEXT, "SLink ID"), timeout=self.WAIT_STD)
            except Exception:
                try:
                    self.safe_click((By.PARTIAL_LINK_TEXT, "Slink ID"))
                except Exception:
                    self.safe_click((By.CSS_SELECTOR, 'a.list-group-item[href*="openid-connect"]'))

            self.ensure_latest_window()

            print("[4] Nhập email, password")
            for loc in [(By.ID, "otherTile"), (By.ID, "otherTileText")]:
                if self.element_exists(loc, timeout=self.WAIT_SHORT):
                    self.safe_click(loc)

            print("[5] Đang nhập email")
            self.wait_sendkeys((By.ID, "i0116"), self.email, timeout=self.WAIT_STD)
            self.safe_click((By.ID, "idSIButton9"), timeout=self.WAIT_STD)

            wait.until(EC.presence_of_element_located((By.ID, "i0118")))

            print("[6] Đang nhập password")
            pwd = self.wait_sendkeys((By.ID, "i0118"), self.password, timeout=self.WAIT_STD)
            pwd.send_keys(Keys.ENTER)
            time.sleep(3)
            if self.element_exists((By.ID, "idSIButton9"), timeout=3):
                try:
                    self.safe_click((By.ID, "idSIButton9"), timeout=self.WAIT_SHORT)
                except Exception:
                    pass

            print("[7] Chọn No")
            if self.element_exists((By.ID, "idBtn_Back"), timeout=10):
                self.safe_click((By.ID, "idBtn_Back"), timeout=self.WAIT_SHORT)

            print("[8] Đợi chuyển về LMS và lấy cookie")
            cookie = self.get_cookie_when_ready(self.LMS_COOKIE_NAME, url_substr="lms.ptit.edu.vn", timeout=self.WAIT_LONG)
            if cookie:
                print("[9] Lấy cookie thành công!!!")
                print(f"[OK] {self.LMS_COOKIE_NAME} = {cookie['value']}")
            else:
                print(f"[!] Không thấy cookie '{self.LMS_COOKIE_NAME}'. In tất cả cookie đang có:")
                for ck in self.driver.get_cookies():
                    print(ck)

            return cookie['value'] if cookie else None

        finally:
            self.driver.quit()

if __name__ == "__main__":
    EMAIL = input("Nhập Email: ").strip()
    PASSWORD = input("Nhập Password: ").strip()
    fetcher = LMSCookieFetcher(EMAIL, PASSWORD, headless=False)
    fetcher.fetch_cookie()