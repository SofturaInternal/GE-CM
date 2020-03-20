import sys
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support.ui import Select
import logging
from selenium.webdriver.chrome.options import Options
logname='cmdb.log'
logging.basicConfig(filename=logname,
                            filemode='a',
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%m/%d/%y %H:%M:%S',
                            level=logging.INFO)

def get_dsrvw_status(edr_value):
	print(type(edr_value))
	print(" This is the edr value")
	options = Options()
	options.add_argument("--headless")
	options.add_argument("--no-sandbox")
	chromedriver = r"./chromedriver"
	driver = webdriver.Chrome(chromedriver , options = options)
	driver.get("http://edr.trans.ge.com/")
        driver.maximize_window()
	singleSSPage = driver.find_element_by_id("innerMonogram")
	singleSSPage.is_displayed()
	userName = driver.find_element_by_id("username")
	userName.clear()
	userName.send_keys("503135589")
	# Enter the password
	password = driver.find_element_by_id("password")
	password.clear()
	password.send_keys("g26Jan@1993m")
	password = driver.find_element_by_id("submitFrm")
	password.click()
	accept = driver.find_element_by_id("legalForm:accept")
	accept.click()
	select = Select(driver.find_element_by_id('legalForm:header:searchObj'))
	# select by visible text
	select.select_by_visible_text('Design Review')
	enterText = driver.find_element_by_id("legalForm:header:searchCrit")
	#Need to pass runtime value
	try:
		enterText.send_keys(int(float(edr_value)))
	except Exception as e:
		print(str(e))
		print('Error : Invalid or Null Input')
		driver.close()
                return "Error Retrieving DSRVW"



	#click
	findButton = driver.find_element_by_xpath("//input[@value='Find']")
	driver.execute_script("arguments[0].click();", findButton)
	# status


	#trs = driver.find_element_by_id("designReview:tolgateRevStep")
	#actualStatus = trs.get_attribute("value")
	#print(actualStatus)

	try:
		reviewStatus = driver.find_element_by_xpath("//input[@class='state_css curnt_state']")
		actualStatus = reviewStatus.get_attribute("value")
		print(actualStatus)
		driver.close()
		return actualStatus
	except UnexpectedAlertPresentException:
		driver.close()
		print "Please Verify the eDR number"
		return "Error Retrieving DSRVW"
