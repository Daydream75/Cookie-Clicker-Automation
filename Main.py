import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip

# Opens the cookie clicker webpage in chrome
cookieClickerURL = 'https://orteil.dashnet.org/cookieclicker/'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("detach", True) # Stops site from closing when program is done
browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chromeOptions)
browser.get(cookieClickerURL)
browser.implicitly_wait(5) # Will wait 5 seconds for an element to appear before throwing an exception error

lastaction = ""

# Saves the game to a file
def saveGame():
    # Checks if option menu is closed and opens it if needed
    optionsButton = browser.find_element(By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")
    if optionsButton.get_attribute("class") != "panelButton selected":
        optionsButton.click()

    # Clicks the export save button
    exportSaveButton = browser.find_element(By.XPATH, "//a[contains(@onclick,'Game.ExportSave()')]")
    exportSaveButton.click()
    
    # Gets the save data and writes it to saveFile.txt
    exportSaveText = browser.find_element(By.XPATH, "//textarea[@id='textareaPrompt']")
    saveFile = open("save.txt", "w")
    saveFile.write(exportSaveText.get_attribute("innerHTML"))
    saveFile.close()

    # Closes the popup
    promptClose = browser.find_element(By.XPATH, "//div[@id='promptClose']")
    promptClose.click()

    # Closes the options menu
    optionsButton = browser.find_element(By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")
    optionsButton.click()

# Loads a saved game file
def loadGame():
    time.sleep(.5)
    optionsButton = browser.find_element(By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")
    if optionsButton.get_attribute("class") != "panelButton selected":
        optionsButton.click()

    # Clicks the import save button
    importSaveButton = browser.find_element(By.XPATH, "//a[contains(@onclick,'Game.ImportSave()')]")
    importSaveButton.click()

    # Adds the save data to the clipboard and then pastes it to the site
    pyperclip.copy(open("save.txt", "r").read())
    importSaveText = browser.find_element(By.XPATH, "//textarea[@id='textareaPrompt']")
    importSaveText.send_keys(Keys.CONTROL + 'v')

    # Hits the load button
    loadButton = browser.find_element(By.XPATH, "//a[@id='promptOption0']")
    loadButton.click()

    # Closes the options menu
    optionsButton = browser.find_element(By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")
    optionsButton.click()

# Loops management of the game for a given time
def runLoop(runTime):
    # This while loop repeats the game processes for the given time
    endTime = time.time() + 60 * runTime
    while time.time() < endTime:
        # Try catch will cause loop to continue if a StaleElementReferenceException appears
        try:
            # Tries 5 times to save the game and passes if it can't, prints what went wrong for diagnoses in case of failure
            lastaction = "saving game"
            for i in range(5):
                try:
                    saveGame()
                    break
                except Exception as error:
                    print("Save failed - " + error)
                    pass

            # Clicks the main cookie 500 times
            lastaction = "clicking cookie"
            time.sleep(.1)
            cookie = browser.find_element(By.XPATH, "//BUTTON[@id='bigCookie']")
            for i in range(500):
                cookie.click()
                time.sleep(.01)

            # Checks if any upgrades can be purchased and then buys them
            lastaction = "buying upgrades"
            time.sleep(.1)
            try:
                upgrade0 = browser.find_element(By.XPATH, "//div[@id='upgrade0']")
                while upgrade0.get_attribute("class") == "crate upgrade enabled":
                    upgrade0.click()
                    time.sleep(.1)
                    upgrade0 = browser.find_element(By.XPATH, "//div[@id='upgrade0']")
            except NoSuchElementException:
                pass

            # For each product that can be bought, buys as many as possible
            lastaction = "buying products"
            time.sleep(.1)
            try:
                products = browser.find_elements(By.XPATH, "//div[@class='product unlocked enabled']")
                for i in range(len(products)-1,-1,-1):
                    while products[i].get_attribute("class") == "product unlocked enabled":
                        products[i].click()
                        time.sleep(.1)
            except NoSuchElementException:
                pass
        except StaleElementReferenceException:
            print("Stale Exception Thrown at " +  lastaction)
            pass

# Closes a popup before game can start with a check in case it doesn't appear
try:
    languageSelect = browser.find_element(By.XPATH, "//DIV[@id='langSelect-EN']")
    languageSelect.click()
except TimeoutException:
    pass

# Checks if there is a save game in the folder and loads it to the website if it exists
if os.path.isfile("save.txt"):
    try:
        loadGame()
    except StaleElementReferenceException:
        loadGame()

# Runs the game for 15 hours. Since it saves every loop, it can be stopped at any time with no progress lost
runLoop(900)