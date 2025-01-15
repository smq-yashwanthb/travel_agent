from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging

class BookingAutomation:
    def __init__(self, headless=False):
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--disable-notifications')
        self.driver = None
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='booking_automation.log'
        )
        self.logger = logging.getLogger(__name__)

    def start_browser(self):
        """Start browser session"""
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.wait = WebDriverWait(self.driver, 20)
            self.logger.info("Browser started successfully")
        except Exception as e:
            self.logger.error(f"Error starting browser: {str(e)}")
            raise

    def close_browser(self):
        """Close browser session"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")

    def search_buses(self, source, destination, date):
        """Search for buses on RedBus"""
        try:
            self.driver.get("https://www.redbus.in")
            
            # Fill source
            source_input = self.wait.until(EC.presence_of_element_located((By.ID, "src")))
            source_input.send_keys(source)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "selected"))).click()

            # Fill destination
            dest_input = self.driver.find_element(By.ID, "dest")
            dest_input.send_keys(destination)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "selected"))).click()

            # Set date
            date_input = self.driver.find_element(By.ID, "onward_cal")
            date_input.click()
            self.select_date(date)

            # Click search
            search_button = self.driver.find_element(By.ID, "search_btn")
            search_button.click()

            # Wait for results and extract data
            time.sleep(5)  # Wait for dynamic content to load
            return self.extract_bus_results()

        except Exception as e:
            self.logger.error(f"Error searching buses: {str(e)}")
            return []

    def extract_bus_results(self):
        """Extract bus search results"""
        buses = []
        try:
            bus_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "bus-item"))
            )

            for bus in bus_elements[:10]:  # Get first 10 results
                bus_data = {
                    'operator': bus.find_element(By.CLASS_NAME, "travels").text,
                    'departure': bus.find_element(By.CLASS_NAME, "dep-time").text,
                    'arrival': bus.find_element(By.CLASS_NAME, "arr-time").text,
                    'duration': bus.find_element(By.CLASS_NAME, "dur").text,
                    'fare': bus.find_element(By.CLASS_NAME, "fare").text,
                    'available_seats': bus.find_element(By.CLASS_NAME, "seat-available").text,
                    'rating': self.extract_rating(bus),
                    'booking_url': bus.get_attribute("data-url")
                }
                buses.append(bus_data)

            self.logger.info(f"Extracted {len(buses)} bus results")
            return buses

        except Exception as e:
            self.logger.error(f"Error extracting bus results: {str(e)}")
            return []

    def book_bus(self, bus_url, passenger_details):
        """Book a bus ticket"""
        try:
            self.driver.get(bus_url)
            
            # Select seats
            seat_layout = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "seat-layout"))
            )
            available_seats = seat_layout.find_elements(By.CLASS_NAME, "available")
            if available_seats:
                available_seats[0].click()  # Select first available seat

            # Fill passenger details
            self.fill_passenger_details(passenger_details)

            # Proceed to payment
            proceed_button = self.driver.find_element(By.ID, "payment-btn")
            proceed_button.click()

            # Wait for payment page and get URL
            time.sleep(5)
            payment_url = self.driver.current_url
            
            self.logger.info(f"Successfully initiated bus booking: {payment_url}")
            return payment_url

        except Exception as e:
            self.logger.error(f"Error booking bus: {str(e)}")
            return None

    def search_hotels(self, location, check_in, check_out):
        """Search for hotels on Booking.com"""
        try:
            self.driver.get("https://www.booking.com")
            
            # Fill location
            location_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "ss"))
            )
            location_input.send_keys(location)
            time.sleep(2)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-suggestion"))).click()

            # Set dates
            self.set_hotel_dates(check_in, check_out)

            # Search
            search_button = self.driver.find_element(By.CLASS_NAME, "search-button")
            search_button.click()

            # Wait for results and extract
            time.sleep(5)
            return self.extract_hotel_results()

        except Exception as e:
            self.logger.error(f"Error searching hotels: {str(e)}")
            return []

    def extract_hotel_results(self):
        """Extract hotel search results"""
        hotels = []
        try:
            hotel_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "hotel-item"))
            )

            for hotel in hotel_elements[:10]:
                hotel_data = {
                    'name': hotel.find_element(By.CLASS_NAME, "hotel-name").text,
                    'rating': hotel.find_element(By.CLASS_NAME, "rating").text,
                    'price': hotel.find_element(By.CLASS_NAME, "price").text,
                    'location': hotel.find_element(By.CLASS_NAME, "location").text,
                    'booking_url': hotel.get_attribute("data-url")
                }
                hotels.append(hotel_data)

            self.logger.info(f"Extracted {len(hotels)} hotel results")
            return hotels

        except Exception as e:
            self.logger.error(f"Error extracting hotel results: {str(e)}")
            return []

    def book_hotel(self, hotel_url, booking_details):
        """Book a hotel"""
        try:
            self.driver.get(hotel_url)
            
            # Select room type
            room_select = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "room-select"))
            )
            room_select.click()

            # Fill booking details
            self.fill_hotel_booking_details(booking_details)

            # Proceed to payment
            book_button = self.driver.find_element(By.CLASS_NAME, "book-button")
            book_button.click()

            # Wait for payment page and get URL
            time.sleep(5)
            payment_url = self.driver.current_url
            
            self.logger.info(f"Successfully initiated hotel booking: {payment_url}")
            return payment_url

        except Exception as e:
            self.logger.error(f"Error booking hotel: {str(e)}")
            return None

    def monitor_price(self, search_params, threshold_price):
        """Monitor prices and alert if below threshold"""
        while True:
            try:
                current_prices = self.search_prices(search_params)
                min_price = min(current_prices)
                
                if min_price <= threshold_price:
                    self.send_price_alert(min_price, search_params)
                    break
                
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error monitoring prices: {str(e)}")
                break

    def compare_fares(self, source, destination, date):
        """Compare fares across different providers"""
        fares = {
            'redbus': self.get_redbus_fares(source, destination, date),
            'abhibus': self.get_abhibus_fares(source, destination, date),
            'others': self.get_other_fares(source, destination, date)
        }
        return self.analyze_fares(fares)

    def wait_for_payment_completion(self, payment_url):
        """Wait and monitor payment completion"""
        try:
            self.driver.get(payment_url)
            max_wait_time = 900  # 15 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                if self.is_payment_completed():
                    booking_confirmation = self.extract_booking_confirmation()
                    self.logger.info("Payment completed successfully")
                    return booking_confirmation
                time.sleep(5)
            
            self.logger.warning("Payment timeout reached")
            return None
            
        except Exception as e:
            self.logger.error(f"Error waiting for payment: {str(e)}")
            return None

    def is_payment_completed(self):
        """Check if payment is completed"""
        try:
            success_elements = self.driver.find_elements(By.CLASS_NAME, "payment-success")
            return len(success_elements) > 0
        except:
            return False

    def extract_booking_confirmation(self):
        """Extract booking confirmation details"""
        try:
            confirmation = {
                'booking_id': self.find_element_text("booking-id"),
                'pnr': self.find_element_text("pnr-number"),
                'amount': self.find_element_text("total-amount"),
                'status': "Confirmed"
            }
            return confirmation
        except Exception as e:
            self.logger.error(f"Error extracting booking confirmation: {str(e)}")
            return None

    def find_element_text(self, class_name):
        """Utility method to find element text"""
        try:
            element = self.driver.find_element(By.CLASS_NAME, class_name)
            return element.text
        except:
            return None