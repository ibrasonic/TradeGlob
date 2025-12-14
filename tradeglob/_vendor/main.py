import datetime
import enum
import json
import logging
import os
import pickle
import random
import re
import shutil
import string
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from websocket import create_connection
import sys

logger = logging.getLogger(__name__)


class Interval(enum.Enum):
    in_1_minute = "1"
    in_3_minute = "3"
    in_5_minute = "5"
    in_15_minute = "15"
    in_30_minute = "30"
    in_45_minute = "45"
    in_1_hour = "1H"
    in_2_hour = "2H"
    in_3_hour = "3H"
    in_4_hour = "4H"
    in_6_hour = "6H"
    in_8_hour = "8H"
    in_12_hour = "12H"
    in_daily = "1D"
    in_weekly = "1W"
    in_monthly = "1M"


class TvDatafeed:
    path = os.path.join(os.path.expanduser("~"), ".tv_datafeed/")
    headers = json.dumps({"Origin": "https://data.tradingview.com"})

    def __save_token(self, token):
        tokenfile = os.path.join(self.path, "token")
        contents = dict(
            token=token,
            date=self.token_date,
            chromedriver_path=self.chromedriver_path,
        )

        with open(tokenfile, "wb") as f:
            pickle.dump(contents, f)

        logger.debug("auth saved")

    def __load_token(self):
        tokenfile = os.path.join(self.path, "token")
        token = None
        if os.path.exists(tokenfile):
            with open(tokenfile, "rb") as f:
                contents = pickle.load(f)

            if contents["token"] not in [
                "unauthorized_user_token",
                None,
            ]:
                token = contents["token"]
                self.token_date = contents["date"]
                logger.debug("auth loaded")

            # Don't load old chromedriver path - always reinstall to match Chrome
            # self.chromedriver_path = contents["chromedriver_path"]

        return token

    def __assert_dir(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            self.__save_token(token=None)

        # Always install/update chromedriver to match current Chrome version
        # Ignore any cached path - always detect and use the compatible version
        logger.info("Detecting Chrome version and installing compatible chromedriver...")
        self.__install_chromedriver()

        if not os.path.exists(self.profile_dir):
            os.mkdir(self.profile_dir)
            logger.debug("created chrome user dir")

    def __install_chromedriver(self):
        try:
            import chromedriver_autoinstaller
        except ImportError:
            logger.info("Installing chromedriver-autoinstaller...")
            os.system("pip install -q chromedriver-autoinstaller")
            import chromedriver_autoinstaller

        # Clear chromedriver-autoinstaller cache to force fresh download
        cache_dirs = [
            os.path.join(os.path.expanduser("~"), ".wdm", "drivers", "chromedriver"),
            os.path.join(os.path.expanduser("~"), ".cache", "selenium", "chromedriver")
        ]
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                try:
                    shutil.rmtree(cache_dir)
                    logger.debug(f"Cleared chromedriver cache: {cache_dir}")
                except:
                    pass

        # Clear old cached chromedriver in .tv_datafeed
        cached_driver = os.path.join(self.path, "chromedriver.exe" if os.name == "nt" else "chromedriver")
        if os.path.exists(cached_driver):
            try:
                os.remove(cached_driver)
                logger.debug("Removed old cached chromedriver")
            except:
                pass

        # Force fresh download to match current Chrome version
        logger.info("Downloading chromedriver to match Chrome version...")
        try:
            # Force check by clearing version tracking
            self.chromedriver_path = chromedriver_autoinstaller.install(True)
        except Exception as e:
            # Fallback to normal install
            logger.debug(f"Install with force failed, trying normal install: {e}")
            try:
                self.chromedriver_path = chromedriver_autoinstaller.install()
            except Exception as e2:
                logger.error(f"Unable to download chromedriver automatically: {e2}")

    def clear_cache(self):

        import shutil

        shutil.rmtree(self.path)
        logger.info("cache cleared")

    def __init__(
        self,
        username=None,
        password=None,
        chromedriver_path=None,
        auto_login=True,
    ) -> None:

        self.ws_debug = False
        self.__automatic_login = auto_login
        self.chromedriver_path = chromedriver_path
        self.profile_dir = os.path.join(self.path, "chrome")
        self.token_date = datetime.date.today() - datetime.timedelta(days=1)
        self.__assert_dir()

        token = None
        token = self.auth(username, password)

        if token is None:
            token = "unauthorized_user_token"
            logger.warning(
                "you are using nologin method, data you access may be limited"
            )

        self.token = token
        self.ws = None
        self.session = self.__generate_session()
        self.chart_session = self.__generate_chart_session()

    def __login(self, username, password):

        driver = self.__webdriver_init()

        if self.__automatic_login:
            try:
                logger.debug("click sign in")
                driver.find_element(By.CLASS_NAME, "tv-header__user-menu-button").click()
                driver.find_element(By.XPATH,
                    '//*[@id="overlap-manager-root"]/div/span/div[1]/div/div/div[1]/div[2]/div'
                ).click()

                time.sleep(5)
                logger.debug("click email")
                embutton = driver.find_element(By.CLASS_NAME,
                    "tv-signin-dialog__toggle-email"
                )
                embutton.click()
                time.sleep(5)

                logger.debug("entering credentials")
                username_input = driver.find_element(By.NAME, "username")
                username_input.send_keys(username)
                password_input = driver.find_element(By.NAME, "password")
                password_input.send_keys(password)

                logger.debug("click login")
                submit_button = driver.find_element(By.CLASS_NAME, "tv-button__loader")
                submit_button.click()
                time.sleep(5)
            except Exception as e:
                logger.error(f"{e}, {e.args}")
                logger.error(
                    "automatic login failed\n Reinitialize tvdatafeed with auto_login=False "
                )

        return driver

    def auth(self, username, password):
        token = self.__load_token()

        if (
            token is None
            and (username is None or password is None)
            and self.__automatic_login
        ):
            pass

        elif self.token_date == datetime.date.today():
            logger.debug("Using cached token from today")
            pass

        elif token is not None and (username is None or password is None):
            logger.debug("Token exists but expired, refreshing...")
            driver = self.__webdriver_init()
            if driver is not None:
                token = self.__get_token(driver)
                if token is not None:
                    self.token_date = datetime.date.today()
                    self.__save_token(token)
                else:
                    logger.error("Failed to extract token after browser login")

        else:
            logger.debug("Performing new login...")
            driver = self.__login(username, password)
            if driver is not None:
                token = self.__get_token(driver)
                if token is not None:
                    self.token_date = datetime.date.today()
                    self.__save_token(token)
                else:
                    logger.error("Failed to extract token after browser login")

        return token

    def __webdriver_init(self):
        caps = DesiredCapabilities.CHROME

        caps["goog:loggingPrefs"] = {"performance": "ALL"}

        logger.info("refreshing tradingview token using selenium")
        logger.debug("launching chrome")
        options = Options()

        if self.__automatic_login:
            options.add_argument("--headless")
            logger.debug("chromedriver in headless mode")

        # Performance optimizations for faster startup
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Reduce initial load
        options.add_argument("--disk-cache-size=1")
        options.page_load_strategy = 'eager'  # Don't wait for full page load

        # special workaround for linux
        if sys.platform == "linux":
            options.add_argument(
                f'--user-data-dir={os.path.expanduser("~")}/snap/chromium/common/chromium/Default'
            )
        # special workaround for macos. Credits "Ambooj"
        elif sys.platform == "darwin":
            options.add_argument(
                f'--user-data-dir={os.path.expanduser("~")}/Library/Application Support/Google/Chrome'
            )
        else:
            options.add_argument(f"user-data-dir={self.profile_dir}")

        driver = None
        try:
            # Python 3.12 + Selenium 4.x: Use service parameter instead of executable_path
            from selenium.webdriver.chrome.service import Service
            service = Service(executable_path=self.chromedriver_path)
            
            # Enable performance logging to capture websocket frames
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            
            driver = webdriver.Chrome(service=service, options=options)

            logger.debug("Opening TradingView login page...")
            driver.set_window_size(1920, 1080)
            
            if not self.__automatic_login:
                # Navigate directly to login page
                driver.get("https://www.tradingview.com/accounts/signin/")
                
                timeout = 300  # 5 minutes timeout
                start_time = time.time()
                logged_in = False
                
                # Quick poll to detect instant redirect if already logged in
                for _ in range(5):  # Check 5 times over 1 second
                    time.sleep(0.2)
                    current_url = driver.current_url
                    if not any(x in current_url for x in ['/accounts/signin', '/accounts/signup', '/signup']):
                        logged_in = True
                        break
                
                # Check if already logged in
                if logged_in:
                    print("✅ Already logged in! Extracting token...\n")
                    logger.info("Already authenticated - session detected")
                    logged_in = True
                else:
                    # Not logged in yet, wait for user to complete login
                    print("   📝 Please complete the login in the browser...\n")
                    
                    while (time.time() - start_time) < timeout:
                        try:
                            current_url = driver.current_url
                            
                            # Simple detection: If we're no longer on the login/signup pages, user logged in
                            if not any(x in current_url for x in ['/accounts/signin', '/accounts/signup', '/signup']):
                                # Give it a tiny moment to ensure redirect is complete
                                time.sleep(0.3)
                                
                                # Verify we're still not on auth pages
                                recheck_url = driver.current_url
                                if not any(x in recheck_url for x in ['/accounts/signin', '/accounts/signup', '/signup']):
                                    logger.info(f"Login confirmed after {int(time.time() - start_time)} seconds")
                                    logged_in = True
                                    break
                        except:
                            pass
                        
                        time.sleep(0.2)  # Check every 0.2 seconds for instant detection
                
                if not logged_in:
                    logger.warning(f"Login timeout after {int(time.time() - start_time)} seconds")
            else:
                # Automatic login mode (with credentials)
                driver.get("https://in.tradingview.com")
                time.sleep(2)  # Reduced from 5 to 2 seconds

            return driver

        except Exception as e:
            if driver is not None:
                driver.quit()
            logger.error(e)
            return None

    @staticmethod
    def __get_token(driver: webdriver.Chrome):
        logger.info("Navigating to chart page to capture token...")
        driver.get("https://www.tradingview.com/chart/")

        def process_browser_logs_for_network_events(logs):
            for entry in logs:
                try:
                    log = json.loads(entry["message"])["message"]

                    if "Network.webSocketFrameSent" in log["method"]:
                        payload = log.get("params", {}).get("response", {}).get("payloadData", "")
                        if (
                            "set_auth_token" in payload
                            and "unauthorized_user_token" not in payload
                        ):
                            yield log
                    # Also check for webSocketFrameReceived
                    elif "Network.webSocketFrameReceived" in log["method"]:
                        payload = log.get("params", {}).get("response", {}).get("payloadData", "")
                        if (
                            "set_auth_token" in payload
                            and "unauthorized_user_token" not in payload
                        ):
                            yield log
                except:
                    continue

        # Aggressive token extraction - check immediately and frequently
        token = None
        wait_times = [1, 1, 1, 2, 2, 3]  # Rapid checks, total up to 10 seconds max
        
        for attempt, wait_time in enumerate(wait_times, 1):
            time.sleep(wait_time)
            
            try:
                logs = driver.get_log("performance")
                events = list(process_browser_logs_for_network_events(logs))
                
                for event in events:
                    try:
                        payload = event["params"]["response"]["payloadData"]
                        # Parse websocket message format: ~m~<length>~m~<json>
                        token_data = payload.split("~m~")[-1]
                        parsed = json.loads(token_data)
                        
                        # Extract token from payload structure
                        if isinstance(parsed, dict) and "p" in parsed:
                            token = parsed["p"][0]
                        elif isinstance(parsed, list) and len(parsed) > 0:
                            token = parsed[0]
                        
                        if token and token != "unauthorized_user_token":
                            logger.info(f"Token extracted successfully")
                            driver.quit()
                            return token
                    except:
                        continue
                    
            except Exception as e:
                logger.error(f"Error retrieving logs: {e}")

        # Token extraction failed
        logger.error("❌ Failed to extract token after all attempts")
        driver.quit()
        return None

    def __create_connection(self):
        logging.debug("creating websocket connection")
        self.ws = create_connection(
            "wss://data.tradingview.com/socket.io/websocket", headers=self.headers
        )

    @staticmethod
    def __filter_raw_message(text):
        try:
            found = re.search('"m":"(.+?)",', text).group(1)
            found2 = re.search('"p":(.+?"}"])}', text).group(1)

            return found, found2
        except AttributeError:
            logger.error("error in filter_raw_message")

    @staticmethod
    def __generate_session():
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "qs_" + random_string

    @staticmethod
    def __generate_chart_session():
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "cs_" + random_string

    @staticmethod
    def __prepend_header(st):
        return "~m~" + str(len(st)) + "~m~" + st

    @staticmethod
    def __construct_message(func, param_list):
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def __create_message(self, func, paramList):
        return self.__prepend_header(self.__construct_message(func, paramList))

    def __send_message(self, func, args):
        m = self.__create_message(func, args)
        if self.ws_debug:
            print(m)
        self.ws.send(m)

    @staticmethod
    def __create_df(raw_data, symbol):
        try:
            out = re.search(r'"s":\[(.+?)\}\]', raw_data).group(1)
            x = out.split(',{"')
            data = list()

            for xi in x:
                xi = re.split(r"\[|:|,|\]", xi)
                ts = datetime.datetime.fromtimestamp(float(xi[4]))
                data.append(
                    [
                        ts,
                        float(xi[5]),
                        float(xi[6]),
                        float(xi[7]),
                        float(xi[8]),
                        float(xi[9]),
                    ]
                )

            data = pd.DataFrame(
                data, columns=["datetime", "open", "high", "low", "close", "volume"]
            ).set_index("datetime")
            data.insert(0, "symbol", value=symbol)
            return data
        except AttributeError:
            logger.error("no data, please check the exchange and symbol")

    @staticmethod
    def __format_symbol(symbol, exchange, contract: int = None):

        if ":" in symbol:
            pass
        elif contract is None:
            symbol = f"{exchange}:{symbol}"

        elif isinstance(contract, int):
            symbol = f"{exchange}:{symbol}{contract}!"

        else:
            raise ValueError("not a valid contract")

        return symbol

    def get_hist(
        self,
        symbol: str,
        exchange: str = "NSE",
        interval: Interval = Interval.in_daily,
        n_bars: int = 10,
        fut_contract: int = None,
        extended_session: bool = False,
    ) -> pd.DataFrame:
        """get historical data

        Args:
            symbol (str): symbol name
            exchange (str, optional): exchange, not required if symbol is in format EXCHANGE:SYMBOL. Defaults to None.
            interval (str, optional): chart interval. Defaults to 'D'.
            n_bars (int, optional): no of bars to download, max 5000. Defaults to 10.
            fut_contract (int, optional): None for cash, 1 for continuous current contract in front, 2 for continuous next contract in front . Defaults to None.
            extended_session (bool, optional): regular session if False, extended session if True, Defaults to False.

        Returns:
            pd.Dataframe: dataframe with sohlcv as columns
        """
        symbol = self.__format_symbol(
            symbol=symbol, exchange=exchange, contract=fut_contract
        )

        interval = interval.value

        self.__create_connection()

        self.__send_message("set_auth_token", [self.token])
        self.__send_message("chart_create_session", [self.chart_session, ""])
        self.__send_message("quote_create_session", [self.session])
        self.__send_message(
            "quote_set_fields",
            [
                self.session,
                "ch",
                "chp",
                "current_session",
                "description",
                "local_description",
                "language",
                "exchange",
                "fractional",
                "is_tradable",
                "lp",
                "lp_time",
                "minmov",
                "minmove2",
                "original_name",
                "pricescale",
                "pro_name",
                "short_name",
                "type",
                "update_mode",
                "volume",
                "currency_code",
                "rchp",
                "rtc",
            ],
        )

        self.__send_message(
            "quote_add_symbols", [self.session, symbol, {"flags": ["force_permission"]}]
        )
        self.__send_message("quote_fast_symbols", [self.session, symbol])

        self.__send_message(
            "resolve_symbol",
            [
                self.chart_session,
                "symbol_1",
                '={"symbol":"'
                + symbol
                + '","adjustment":"splits","session":'
                + ('"regular"' if not extended_session else '"extended"')
                + "}",
            ],
        )
        self.__send_message(
            "create_series",
            [self.chart_session, "s1", "s1", "symbol_1", interval, n_bars],
        )
        self.__send_message("switch_timezone", [self.chart_session, "exchange"])

        raw_data = ""

        logger.debug(f"getting data for {symbol}...")
        while True:
            try:
                result = self.ws.recv()
                raw_data = raw_data + result + "\n"
            except Exception as e:
                logger.error(e)
                break

            if "series_completed" in result:
                break

        return self.__create_df(raw_data, symbol)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    tv = TvDatafeed(
        # auto_login=False,
    )
    print(tv.get_hist("CRUDEOIL", "MCX", fut_contract=1))
    print(tv.get_hist("NIFTY", "NSE", fut_contract=1))
    print(
        tv.get_hist(
            "EICHERMOT",
            "NSE",
            interval=Interval.in_1_hour,
            n_bars=500,
            extended_session=False,
        )
    )
