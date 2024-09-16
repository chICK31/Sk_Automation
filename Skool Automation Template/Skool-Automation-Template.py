from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

#Note that this only works for CSjoseph Skool, it doesn't work on other Skool Classrooms

Email = "INSERT_EMAIL_HERE"
Password = "INSERT_PASSWORD_HERE"
total_pages = 15  # You can change this number based on how many total pages you need to iterate through in the Skool website

#You could change the "time.sleep" values if you want to make it go faster or slower depending on what works for you

# Step 1: Setup WebDriver for Chrome
driver_path = r'INSERT_DRIVER_PATH'  # Update this to your actual ChromeDriver path
Chrome_path = r'INSERT_CHROME_PATH'  # Update this to Chrome browser path

# Configure options to use Chrome
options = Options()
options.binary_location = Chrome_path

# Use Service object to pass the executable path for ChromeDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Function to log in the first time
def login(driver):
    driver.get('https://www.skool.com/csjoseph/about')
    
    # Step 3: Press the "Log In" button
    login_button = driver.find_element(By.XPATH, '//button[@type="button" and span[text()="Log In"]]')
    login_button.click()
    
    # Step 4: Fill in the email input field
    time.sleep(1)  # Wait for the input field to appear
    email_input = driver.find_element(By.ID, "email")
    email_input.clear()  # Clear the input field first
    email_input.send_keys(Email)  # Input the email

    # Step 5: Fill in the password input field
    password_input = driver.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys(Password)  # Input the password

    # Step 6: Press the "Log In" button to submit the form
    login_submit_button = driver.find_element(By.XPATH, '//button[@type="submit" and span[text()="Log In"]]')
    login_submit_button.click()

    # Step 7: Wait for the login process to complete
    time.sleep(5)  # Adjust this based on your internet speed

# Function to close alert if visible
def close_alert_if_visible(driver):
    try:
        close_button = driver.find_element(By.XPATH, '//button[@data-test-id="alert-close-button"]')
        close_button.click()
        print("Alert close button found and clicked!")
        time.sleep(0.5)  # Small delay to allow the alert to disappear
        return True  # Return True if the alert was closed
    except Exception:
        return False  # If no alert was found

# Function to click the specific image if visible
def click_image_if_visible(driver):
    try:
        image_element = driver.find_element(By.XPATH, '//img[@alt="C.S. Joseph" and contains(@class, "styled__AsideGroupCardImage-sc-1qg8wku-3")]')
        image_element.click()
        print("Image clicked!")
        time.sleep(0.5)  # Small delay to ensure the action is performed
    except Exception as e:
        print(f"Image not found or could not be clicked: {str(e)}")

# Function to check if a string contains a single string of characters without dashes or spaces
def is_single_string_without_dashes_or_spaces(url_part):
    return url_part.isalnum() and '-' not in url_part and ' ' not in url_part

# Function to process the page and handle likes and replies
def process_page(driver, sub_urls):
    # Skip specific URLs
# Updated list of URLs to skip
    skip_urls = [
        'https://www.skool.com/csjoseph/-/members', 
        'https://www.skool.com/csjoseph/-/leaderboards',
        'https://www.skool.com/csjoseph/classroom',
        'https://www.skool.com/csjoseph/calendar',
        'https://www.skool.com/csjoseph/about',
        'https://www.skool.com/csjoseph/calendar?eid=9b3da5a62876490d921ec361c4b6c3fc&eoid=1726624800',
        "https://csjoseph.life/coaching",
        "https://www.skool.com/csjoseph/verified"
    ]

    for url in sub_urls:
        url_parts = url.split('/')
        
        # Skip URLs with "@" or in the skip list
        if any(skip_url in url for skip_url in skip_urls) or '@' in url:
            print(f"Skipping URL: {url}")
            continue

        # Check if the URL part is either a dash-containing URL or a single string of characters without spaces or dashes
        if any('-' in part for part in url_parts) or any(is_single_string_without_dashes_or_spaces(part) for part in url_parts):
            print(f"Visiting URL: {url}")
            driver.get(url)  # Visit the URL
            time.sleep(2)  # Wait for the page to load

            # Press the "View more replies" button if found
            while True:
                close_alert_if_visible(driver)
                try:
                    view_more_button = driver.find_element(By.XPATH, '//div[contains(@class, "styled__ExpandRepliesLabel-sc-1lql1qn-9")]')
                    print("Pressing 'View more replies' button")
                    view_more_button.click()
                    time.sleep(2)
                    click_image_if_visible(driver)  # Click image after pressing the button
                except Exception:
                    print("No more 'View more replies' buttons found")
                    break

            # Handle Like buttons
            try:
                like_buttons = driver.find_elements(By.XPATH, '//button[contains(@class, "styled__LikeButton-sc-ne2b7k-1")]')
                for like_button in like_buttons:
                    close_alert_if_visible(driver)
                    label_text = like_button.find_element(By.XPATH, './div[contains(@class, "styled__LikeLabel-sc-ne2b7k-3")]').text
                    if 'Like' in label_text and 'Liked' not in label_text:
                        print("Pressing 'Like' button (not liked yet)")
                        like_button.click()
                        time.sleep(1)
                    else:
                        print("'Like' button already pressed or not applicable")
            except Exception as e:
                print(f"Error handling 'Like' buttons: {str(e)}")

            # Handle Vote buttons and retry if alert is closed
            try:
                vote_buttons = driver.find_elements(By.XPATH, '//button[contains(@class, "styled__VoteButton-sc-1e3d9on-2")]')
                for vote_button in vote_buttons:
                    close_alert_if_visible(driver)
                    if 'iihqfp' in vote_button.get_attribute("class"):  # If not already voted
                        print("Pressing 'Vote' button (not voted yet)")
                        vote_button.click()
                        time.sleep(1)
                        # If alert closes, try clicking the Vote button again
                        if close_alert_if_visible(driver):
                            print("Retrying 'Vote' button after closing alert")
                            vote_button.click()
                            time.sleep(1)
                    else:
                        print("'Vote' button already pressed or not applicable")
            except Exception as e:
                print(f"Error handling 'Vote' buttons: {str(e)}")

# Log in on the first page visit
login(driver)

# Iterate through each page starting from page 1 (since there are 30 sub-pages per page)

for page_num in range(1, total_pages + 1):
    next_page_url = f'https://www.skool.com/csjoseph?c=&fl=&p={page_num}'
    print(f"Visiting page {page_num}: {next_page_url}")
    driver.get(next_page_url)
    time.sleep(2)

    # Extract URLs from the new page and process them
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    a_tags = soup.find_all('a')
    sub_urls = [urljoin('https://www.skool.com/csjoseph', tag.get('href')) for tag in a_tags if tag.get('href')]

    # Process each URL found on the page
    process_page(driver, sub_urls)

# Close the browser after all pages are processed
driver.quit()