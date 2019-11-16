import urllib.request
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

#Default to craigslist behavior of 120 pages maximum per search
def getCraigsListURLs(pageNumber = 0, url = "https://chicago.craigslist.org/search/apa", listingsPerPage = 120):
	postingUrls = []
	url = url +"?s="+str(pageNumber*120)
	webDriver.get(url)
	allListings = webDriver.find_elements_by_xpath("//ul[@class='rows']/li/a")
	for listing in allListings:
		postingUrls.append(listing.get_attribute("href"))

	return postingUrls


webDriver = webdriver.Chrome()
outputFile = open("listings.csv", 'w', encoding='utf-8')
csvLine = {"Status":"", "URL":"", "Bedrooms":"", "Bathrooms":"", "Price":"", "SqF":"", "Address":"", "PhoneNumber":"", "email":""}

# Write the first line of the file
for entry in csvLine:
	outputFile.write(entry+",")
outputFile.write("\n")

for i in range(25):
	postUrls = getCraigsListURLs(i)
	for url in postUrls:
		csvLine["URL"] = url
		webDriver.get(url)
		try:
			csvLine["Bedrooms"] = webDriver.find_element_by_xpath("//span[@class='shared-line-bubble']/b[1]").text
			csvLine["Bathrooms"] = webDriver.find_element_by_xpath("//span[@class='shared-line-bubble']/b[2]").text
			csvLine["Price"] = webDriver.find_element_by_xpath("//span[@class='price']").text
			csvLine["Sqf"] = ""
			csvLine["Address"] = webDriver.find_element_by_xpath("//div[@class='mapaddress']").text
		except NoSuchElementException:
			#If we cant find the basic info then we just pass and dont even write it
			continue

		try:
			replyButton = webDriver.find_element_by_xpath("//button[@class='reply-button js-only']")
			replyButton.click()
			time.sleep(1)
			csvLine["email"] = webDriver.find_element_by_xpath("//a[@class='mailapp']").text

			showPhoneButton = webDriver.find_element_by_xpath("//button[@class='show-phone']")
			showPhoneButton.click()
			time.sleep(5)
			csvLine["PhoneNumber"] = webDriver.find_element_by_xpath("//span[@id='reply-tel-number']").text
		except NoSuchElementException:
			pass

		for value in csvLine.values():
			outputFile.write(value+',')
		outputFile.write("\n")

outputFile.close()

print("wrote the file")