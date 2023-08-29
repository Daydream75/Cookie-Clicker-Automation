import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
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
browser.implicitly_wait(10)

# Closes a popup before game can start
try:
    languageSelect = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//DIV[@id='langSelect-EN']")))
    languageSelect.click()
except TimeoutException:
    pass

# Saves the game to a file
def saveGame():
    # Checks if option menu is closed and opens it if needed
    optionsButton = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")))
    if optionsButton.get_attribute("class") != "panelButton selected":
        optionsButton.click()

    # Clicks the export save button
    exportSaveButton = WebDriverWait(browser, 2).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@onclick,'Game.ExportSave()')]")))    
    exportSaveButton.click()
    
    # Gets the save data and writes it to saveFile.txt
    exportSaveText = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//textarea[@id='textareaPrompt']")))
    saveFile = open("save.txt", "w")
    saveFile.write(exportSaveText.get_attribute("innerHTML"))
    saveFile.close()

    # Closes the popup
    promptClose = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='promptClose']")))
    promptClose.click()

    # Closes the options menu
    optionsButton = browser.find_element(By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")
    optionsButton.click()

# Loads a saved game file
def loadGame():
    time.sleep(.1)
    optionsButton = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")))
    if optionsButton.get_attribute("class") != "panelButton selected":
        optionsButton.click()

    # Clicks the import save button
    importSaveButton = WebDriverWait(browser, 2).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@onclick,'Game.ImportSave()')]")))    
    importSaveButton.click()

    # Adds the save data to the clipboard and then pastes it to the site
    pyperclip.copy(open("save.txt", "r").read())
    importSaveText = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//textarea[@id='textareaPrompt']")))
    importSaveText.send_keys(Keys.CONTROL + 'v')

    # Hits the load button
    loadButton = browser.find_element(By.XPATH, "//a[@id='promptOption0']")
    loadButton.click()

    # Closes the options menu
    optionsButton = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='prefsButton']/descendant::div[@class='subButton']")))
    optionsButton.click()

# Checks if there is a save game in the folder and loads it to the website if it exists
if os.path.isfile("save.txt"):
    loadGame()

# This while loop repeats the game processes for the given time, 
runTime = 3
endTime = time.time() + 60 * runTime
while time.time() < endTime:    
    # Checks if any upgrades can be purchased and buys them if possible
    upgrade0=WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='upgrade0']")))
    while upgrade0.get_attribute("class") == "crate upgrade enabled":
        upgrade0.click()
        upgrade0=WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='upgrade0']")))

    # For each product that can be bought, buys as many as possible
    products = browser.find_elements(By.XPATH, "//div[@class='product unlocked enabled']")
    for i in range(len(products)-1,-1,-1):
        while products[i].get_attribute("class") == "product unlocked enabled":
            products[i].click()

    # Clicks the main cookie 500 times
    cookie = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//BUTTON[@id='bigCookie']")))
    for i in range(500):
        try:
            cookie.click()
        except StaleElementReferenceException:
            cookie = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//BUTTON[@id='bigCookie']")))
            cookie.click()
        time.sleep(.01)

    # Saves the game
    saveGame()