#! python3
# -*- coding: utf-8 -*-
"""Naukri Daily update - Using Chrome"""
from dotenv import load_dotenv
import os  # Load environment variables from .env file
load_dotenv()
import io
import logging
import os
import sys
import time
from datetime import datetime
from random import choice, randint
from string import ascii_uppercase, digits
import pandas as pd
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager as CM
import io
from random import randint
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io 
from random import randint
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from bs4 import BeautifulSoup# Add folder Path of your resume

# Add folder Path of your resume
originalResumePath = "original_resume.pdf"
# Add Path where modified resume should be saved
modifiedResumePath = "modified_resume.pdf"



# Fetch credentials from environment
username = os.getenv("NAUKRI_USERNAME")
password = os.getenv("NAUKRI_PASSWORD")
mob = os.getenv("NAUKRI_MOBILE")
name = os.getenv("NAUKRI_NAME")
# False if you dont want to add Random HIDDEN chars to your resume
updatePDF = True

# If Headless = True, script runs Chrome in headless mode without visible GUI
headless = False
keywords = ['python developer']
location = ''
firstname = 'Dinesh'
lastname = 'Suthar'
maxcount = 100
applied = 0
failed = 0
applied_list = {'passed': [], 'failed': []}
csv_file = "naukriapplied.csv"
# ----- No other changes required -----
freshness=7
experience =3
start_page=1
end_page=6
NaukriURL = "https://www.naukri.com/nlogin/login"

logging.basicConfig(
    level=logging.INFO, filename="naukri.log", format="%(asctime)s    : %(message)s"
)
# logging.disable(logging.CRITICAL)
os.environ["WDM_LOCAL"] = "1"
os.environ["WDM_LOG_LEVEL"] = "0"


def log_msg(message):
    """Print to console and store to Log"""
    print(message)
    logging.info(message)


def catch(error):
    """Method to catch errors and log error details"""
    _, _, exc_tb = sys.exc_info()
    lineNo = str(exc_tb.tb_lineno)
    msg = "%s : %s at Line %s." % (type(error), error, lineNo)
    print(msg)
    logging.error(msg)


def getObj(locatorType):
    """This map defines how elements are identified"""
    map = {
        "ID": By.ID,
        "NAME": By.NAME,
        "XPATH": By.XPATH,
        "TAG": By.TAG_NAME,
        "CLASS": By.CLASS_NAME,
        "CSS": By.CSS_SELECTOR,
        "LINKTEXT": By.LINK_TEXT,
    }
    return map[locatorType.upper()]


def GetElement(driver, elementTag, locator="ID"):
    """Wait max 15 secs for element and then select when it is available"""
    try:

        def _get_element(_tag, _locator):
            _by = getObj(_locator)
            if is_element_present(driver, _by, _tag):
                return WebDriverWait(driver, 15).until(
                    lambda d: driver.find_element(_by, _tag)
                )

        element = _get_element(elementTag, locator.upper())
        if element:
            return element
        else:
            log_msg("Element not found with %s : %s" % (locator, elementTag))
            return None
    except Exception as e:
        catch(e)
    return None


def is_element_present(driver, how, what):
    """Returns True if element is present"""
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException:
        return False
    return True


def WaitTillElementPresent(driver, elementTag, locator="ID", timeout=30):
    """Wait till element present. Default 30 seconds"""
    result = False
    driver.implicitly_wait(0)
    locator = locator.upper()

    for _ in range(timeout):
        time.sleep(0.99)
        try:
            if is_element_present(driver, getObj(locator), elementTag):
                result = True
                break
        except Exception as e:
            log_msg("Exception when WaitTillElementPresent : %s" % e)
            pass

    if not result:
        log_msg("Element not found with %s : %s" % (locator, elementTag))
    driver.implicitly_wait(3)
    return result


def tearDown(driver):
    try:
        driver.close()
        log_msg("Driver Closed Successfully")
    except Exception as e:
        catch(e)
        pass

    try:
        driver.quit()
        log_msg("Driver Quit Successfully")
    except Exception as e:
        catch(e)
        pass


def randomText():
    return "".join(choice(ascii_uppercase + digits) for _ in range(randint(1, 5)))


def LoadNaukri(headless):
    """Open Chrome to load Naukri.com"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")  # ("--kiosk") for MAC
    options.add_argument("--disable-popups")
    options.add_argument("--disable-gpu")
    
    # If headless mode is enabled, add headless-specific options
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("window-size=1920x1080")
        options.add_argument("--remote-debugging-port=9222")  # Open a debugging port to inspect the browser
        options.add_argument("--disable-software-rasterizer")  # Disable software rendering
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")



    # Initialize the driver using ChromeDriverManager to automatically download the right version
    driver = None
    try:
        log_msg("Attempting to launch Chrome in headless or normal mode...")
        driver = webdriver.Chrome(options=options, service=ChromeService(CM().install()))
    except Exception as e:
        log_msg(f"Error initializing ChromeDriver: {e}")
        driver = webdriver.Chrome(options=options)
    
    log_msg("Google Chrome Launched!")

    driver.implicitly_wait(3)  # Implicit wait for elements to load
    driver.get(NaukriURL)
    log_msg(f"Navigated to {NaukriURL}")

    return driver


def naukriLogin(headless=False):
    """Open Chrome browser and Login to Naukri.com"""
    status = False
    driver = None
    username_locator = "usernameField"
    password_locator = "passwordField"
    login_btn_locator = "//*[@type='submit' and normalize-space()='Login']"
    skip_locator = "//*[text() = 'SKIP AND CONTINUE']"

    try:
        driver = LoadNaukri(headless)
        print(driver.title)
        if "naukri" in driver.title.lower():
            log_msg("Website Loaded Successfully.")

        emailFieldElement = None
        if is_element_present(driver, By.ID, username_locator):
            emailFieldElement = GetElement(driver, username_locator, locator="ID")
            time.sleep(1)
            passFieldElement = GetElement(driver, password_locator, locator="ID")
            time.sleep(1)
            loginButton = GetElement(driver, login_btn_locator, locator="XPATH")
        else:
            log_msg("None of the elements found to login.")

        if emailFieldElement is not None:
            emailFieldElement.clear()
            emailFieldElement.send_keys(username)
            time.sleep(1)
            passFieldElement.clear()
            passFieldElement.send_keys(password)
            time.sleep(1)
            loginButton.send_keys(Keys.ENTER)
            time.sleep(1)

            # Added click to Skip button
            print("Checking Skip button")

            if WaitTillElementPresent(driver, skip_locator, "XPATH", 10):
                GetElement(driver, skip_locator, "XPATH").click()

            # CheckPoint to verify login
            if WaitTillElementPresent(driver, "ff-inventory", locator="ID", timeout=40):
                CheckPoint = GetElement(driver, "ff-inventory", locator="ID")
                if CheckPoint:
                    log_msg("Naukri Login Successful")
                    status = True
                    return (status, driver)
                else:
                    log_msg("Unknown Login Error")
                    return (status, driver)
            else:
                log_msg("Unknown Login Error")
                return (status, driver)

    except Exception as e:
        catch(e)
    return (status, driver)


def UpdateProfile(driver):
    try:
        mobXpath = "//*[@name='mobile'] | //*[@id='mob_number']"
        saveXpath = "//button[@ type='submit'][@value='Save Changes'] | //*[@id='saveBasicDetailsBtn']"
        view_profile_locator = "//*[contains(@class, 'view-profile')]//a"
        edit_locator = "(//*[contains(@class, 'icon edit')])[1]"
        save_confirm = "//*[text()='today' or text()='Today']"
        close_locator = "//*[contains(@class, 'crossIcon')]"
        namexpath = '//*[@id="name"]'

        WaitTillElementPresent(driver, view_profile_locator, "XPATH", 20)
        profElement = GetElement(driver, view_profile_locator, locator="XPATH")
        profElement.click()
        driver.implicitly_wait(2)

        if WaitTillElementPresent(driver, close_locator, "XPATH", 10):
            GetElement(driver, close_locator, locator="XPATH").click()
            time.sleep(2)

        WaitTillElementPresent(driver, edit_locator + " | " + saveXpath, "XPATH", 20)
        if is_element_present(driver, By.XPATH, edit_locator):
            editElement = GetElement(driver, edit_locator, locator="XPATH")
            editElement.click()

            WaitTillElementPresent(driver, namexpath, "XPATH", 20)
            namexpathElement = GetElement(driver, namexpath, locator="XPATH")
            if namexpathElement:
                namexpathElement.clear()
                namexpathElement.send_keys(name)
                driver.implicitly_wait(2)
                
                saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
                saveFieldElement.send_keys(Keys.ENTER)
                driver.implicitly_wait(3)
            else:
                log_msg("Mobile number element not found in UI")


            



            # WaitTillElementPresent(driver, mobXpath, "XPATH", 20)
            # mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            # if mobFieldElement:
            #     mobFieldElement.clear()
            #     mobFieldElement.send_keys(mob)
            #     driver.implicitly_wait(2)
                
            #     saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
            #     saveFieldElement.send_keys(Keys.ENTER)
            #     driver.implicitly_wait(3)
            # else:
            #     log_msg("Mobile number element not found in UI")

            WaitTillElementPresent(driver, save_confirm, "XPATH", 10)
            if is_element_present(driver, By.XPATH, save_confirm):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        elif is_element_present(driver, By.XPATH, saveXpath):
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            if mobFieldElement:
                mobFieldElement.clear()
                mobFieldElement.send_keys(mob)
                driver.implicitly_wait(2)
    
                saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
                saveFieldElement.send_keys(Keys.ENTER)
                driver.implicitly_wait(3)
            else:
                log_msg("Mobile number element not found in UI")

            WaitTillElementPresent(driver, "confirmMessage", locator="ID", timeout=10)
            if is_element_present(driver, By.ID, "confirmMessage"):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        time.sleep(5)

    except Exception as e:
        catch(e)

import io
from random import randint
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def UpdateResume():
    try:
        # Random text with random location and size
        xloc = randint(700, 1000)  # Random X location (out of page)
        fsize = randint(1, 10)  # Random font size

        # Create a new PDF with random text using ReportLab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        # can.setFont("Helvetica", fsize)
        can.drawString(xloc, 100, "lon")  # Random text
        can.save()
        packet.seek(0)

        # Read the new PDF
        new_pdf = PdfReader(packet)

        # Read the existing PDF
        existing_pdf = PdfReader(open(originalResumePath, "rb"))
        pagecount = len(existing_pdf.pages)
        print(f"Found {pagecount} pages in PDF")

        # Prepare the output PDF
        output = PdfWriter()

        # Add all pages except the last one from the existing PDF
        for pageNum in range(pagecount - 1):
            output.add_page(existing_pdf.pages[pageNum])

        # Merge the new PDF with the last page
        last_page = existing_pdf.pages[pagecount - 1]
        last_page.merge_page(new_pdf.pages[0])
        output.add_page(last_page)

        # Save the new PDF to file
        with open(modifiedResumePath, "wb") as outputStream:
            output.write(outputStream)

        print(f"Saved modified PDF: {modifiedResumePath}")
        return os.path.abspath(modifiedResumePath)

    except Exception as e:
        print(f"Error: {e}")
        return os.path.abspath(originalResumePath)

def UploadResume(driver, resumePath):
    try:
        attachCVID = "attachCV"
        CheckPointXpath = "//*[contains(@class, 'updateOn')]"
        saveXpath = "//button[@type='button']"
        close_locator = "//*[contains(@class, 'crossIcon')]"

        driver.get("https://www.naukri.com/mnjuser/profile")

        time.sleep(2)
        if WaitTillElementPresent(driver, close_locator, "XPATH", 10):
            GetElement(driver, close_locator, locator="XPATH").click()
            time.sleep(2)

        WaitTillElementPresent(driver, attachCVID, locator="ID", timeout=10)
        AttachElement = GetElement(driver, attachCVID, locator="ID")
        AttachElement.send_keys(resumePath)

        if WaitTillElementPresent(driver, saveXpath, locator="ID", timeout=5):
            saveElement = GetElement(driver, saveXpath, locator="XPATH")
            saveElement.click()

        WaitTillElementPresent(driver, CheckPointXpath, locator="XPATH", timeout=30)
        CheckPoint = GetElement(driver, CheckPointXpath, locator="XPATH")
        if CheckPoint:
            LastUpdatedDate = CheckPoint.text
            todaysDate1 = datetime.today().strftime("%b %d, %Y")
            todaysDate2 = datetime.today().strftime("%b %#d, %Y")
            if todaysDate1 in LastUpdatedDate or todaysDate2 in LastUpdatedDate:
                log_msg(
                    "Resume Document Upload Successful. Last Updated date = %s"
                    % LastUpdatedDate
                )
            else:
                log_msg(
                    "Resume Document Upload failed. Last Updated date = %s"
                    % LastUpdatedDate
                )
        else:
            log_msg("Resume Document Upload failed. Last Updated date not found.")

    except Exception as e:
        catch(e)
    time.sleep(2)


def ApplyJobs(driver):
    
    global applied, failed
    job_links = []
    print("Starting job application process...")

    for keyword in keywords:
        print(f"Processing keyword: {keyword}")
        for page in range(start_page, end_page):
            if location == '':
                url = f"https://www.naukri.com/{keyword.lower().replace(' ', '-')}-jobs-{str(page + 1)}?wfhType=0&wfhType=2&wfhType=3&jobAge={freshness}&experience={experience}&ctcFilter=10to15&ctcFilter=15to25"
            else:
                url = f"https://www.naukri.com/{keyword.lower().replace(' ', '-')}-jobs-in-{location.lower().replace(' ', '-')}-{str(page + 1)}"
            print(f"Fetching jobs from: {url}")
            driver.get(url)
            print(f"Opened URL: {url}")
            time.sleep(3)
            print("Fetching page source...")
            # print(driver.page_source)
            # with open('ex.html','w') as f:
            #     f.write(driver.page_source)
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            print("Parsing job listings...")
            results = soup.find(class_='styles_job-listing-container__OCfZC')
            # print(results)
            if results:
                print("Job listings found. Extracting job elements...")
                job_elems = results.find_all( class_='srp-jobtuple-wrapper')
                print(f"Found {len(job_elems)} job elements.")
                for job_elem in job_elems:
                    link = job_elem.find('a', class_='title')
                    if link:
                        job_links.append(link.get('href'))
                        print(f"Job link added: {link.get('href')}")
            else:
                print("No job listings found on this page.")
    
    print(f"Total job links fetched: {len(job_links)}")
    
    for idx, link in enumerate(job_links):
        print(f"Processing job {idx + 1}/{len(job_links)}: {link}")
        try:
            driver.get(link)
            time.sleep(3)
            print("Attempting to find 'Apply' button...")
            apply_button = driver.find_element(By.XPATH, "//*[text()='Apply']")
            apply_button.click()
            applied += 1
            applied_list['passed'].append(link)
            print(f"Successfully applied to job: {link}. Total applied: {applied}")
        except Exception as e:
            failed += 1
            applied_list['failed'].append(link)
            error_message = f"Failed to apply for {link}. Error: {e}"
            log_msg(error_message)
            print(error_message)
        
        # Break if max application count is reached
        if applied >= maxcount:
            print("Reached maximum application count. Stopping process.")
            break
    
    print(f"Job application process completed. Total applied: {applied}, Total failed: {failed}")
def main():
    log_msg("-----Naukri.py Script Run Begin-----")
    driver = None
    try:
        status, driver = naukriLogin(headless)
        if status:
            UpdateProfile(driver)
            if os.path.exists(originalResumePath):
                # pass
                if updatePDF:
                    resumePath = UpdateResume()
                    UploadResume(driver, resumePath)
                else:
                    UploadResume(driver, originalResumePath)
            else:
                log_msg("Resume not found at %s " % originalResumePath)
            ApplyJobs(driver)
    except Exception as e:
        catch(e)

    finally:
        if driver:
            tearDown(driver)

    log_msg("-----Naukri.py Script Run Ended-----\n")
    pd.DataFrame.from_dict({k: pd.Series(v) for k, v in applied_list.items()}).to_csv(csv_file, index=False)
    log_msg(f"Saved applied jobs to {csv_file}")

if __name__ == "__main__":
    main()
