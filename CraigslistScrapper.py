import urllib.request
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

#Default to craigslist behavior of 120 pages maximum per search
def getCraigsListURLs(webDriver, pageNumber = 0, url = "https://chicago.craigslist.org/search/apa", listingsPerPage = 120):
	postingUrls = []
	url = url +"?s="+str(pageNumber*120)
	print("Getting listings for "+url)
	webDriver.get(url)
	allListings = webDriver.find_elements_by_xpath("//ul[@class='rows']/li/a")
	for listing in allListings:
		postingUrls.append(listing.get_attribute("href"))

	print("got the list of urls\n")
	return postingUrls

def getPageListingsAndWriteToFile( pageCount ):
	webDriver = webdriver.Chrome()

	postUrls = getCraigsListURLs(webDriver, pageCount)

	for url in postUrls:
		attemptsAtPage = 0
		while attemptsAtPage < 5:
			csvLine["URL"] = url
			webDriver.get(url)
			time.sleep(1)
			try:
				csvLine["Bedrooms"] = webDriver.find_element_by_xpath("//span[@class='shared-line-bubble']/b[1]").text
			except NoSuchElementException:
				pass
			try:
				csvLine["Bathrooms"] = webDriver.find_element_by_xpath("//span[@class='shared-line-bubble']/b[2]").text
			except NoSuchElementException:
				pass
			try:
				csvLine["Price"] = webDriver.find_element_by_xpath("//span[@class='price']").text
			except NoSuchElementException:
				pass
			try:
				csvLine["Sqf"] = ""
			except NoSuchElementException:
				pass
			try:
				csvLine["Address"] = webDriver.find_element_by_xpath("//div[@class='mapaddress']").text
			except NoSuchElementException:
				pass

			replyButton = webDriver.find_element_by_xpath("//button[@class='reply-button js-only']")
			replyButton.click()
			time.sleep(1)

			#Craigslist is cracking down on bots so this hack resubmits
			try:
				errorElement = webDriver.find_element_by_xpath("//div[@class='lbcontent']")
				if "An error has occurred" in errorElement.text:
					attemptsAtPage = attemptsAtPage + 1
					continue
			except NoSuchElementException:
				pass

			try:
				csvLine["email"] = webDriver.find_element_by_xpath("//a[@class='mailapp']").text
			except NoSuchElementException:
				pass

			try:
				showPhoneButton = webDriver.find_element_by_xpath("//button[@class='show-phone']")
				showPhoneButton.click()
				time.sleep(5)
				#Craigslist is cracking down on bots so this hack resubmits
				try:
					errorElement = webDriver.find_element_by_xpath("//div[@class='lbcontent']")
					if "An error has occurred" in errorElement.text:
						attemptsAtPage = attemptsAtPage + 1
						continue
				except NoSuchElementException:
					pass

				csvLine["PhoneNumber"] = webDriver.find_element_by_xpath("//span[@id='reply-tel-number']").text
			except NoSuchElementException:
				pass
			break

		if attemptsAtPage == 3:
			print("Failed to retrieve contact information for URL: "+url)
			failedURLs.write(url+"\n")
		else:
			for value in csvLine.values():
				outputFile.write(value+',')
			outputFile.write("\n")

	webDriver.close()

failedURLs = open("failedListings.txt", 'w', encoding='utf-8')
outputFile = open("listings.csv", 'w', encoding='utf-8')
csvLine = {"Status":"", "URL":"", "Bedrooms":"", "Bathrooms":"", "Price":"", "SqF":"", "Address":"", "PhoneNumber":"", "email":""}

# Write the first line of the file
for entry in csvLine:
	outputFile.write(entry+",")
outputFile.write("\n")


url = "https://chicago.craigslist.org/search/apa"
webScrappingFutures = []
pageCount = 0
pagesToGather =5
maxThreads = 1

runningThreads = []
while(pageCount < pagesToGather):
	for i in range(maxThreads):
		thread = Thread(target=getPageListingsAndWriteToFile, args=(pageCount,))
		thread.start()
		runningThreads.append(thread)
		pageCount = pageCount + 1

	for thread in runningThreads:
		thread.join()

outputFile.close()
failedURLs.close()

print("wrote the file")