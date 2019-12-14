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
	attemptsOfLoadingPage = 0
	notLoadedWebPage = True
	while attemptsOfLoadingPage < 3 and notLoadedWebPage:
			try:
				webDriver.get(url)
				notLoadedWebPage = False
			except:
				attemptsOfLoadingPage  = attemptsOfLoadingPage + 1
	allListings = webDriver.find_elements_by_xpath("//ul[@class='rows']/li/a")
	for listing in allListings:
		postingUrls.append(listing.get_attribute("href"))

	print("got the list of urls\n")
	return postingUrls

#static variable at main name space to see if we are hitting sets
titleSet = set()
addressSet = set()
bedBathPriceSet = set()
emailSet = set()
phoneSet = set()
def getPageListingsAndWriteToFile( pageCount ):
	webDriver = webdriver.Chrome()

	postUrls = getCraigsListURLs(webDriver, pageCount)

	for url in postUrls:
		attemptsAtPage = 0
		global csvLineBlank
		csvLine = csvLineBlank
		while attemptsAtPage < 3:
			attemptsAtPage = attemptsAtPage + 1
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
				csvLine["Full Title"] = webDriver.find_element_by_xpath("//span[@class='postingtitletext']//span[@id='titletextonly'").text
			except NoSuchElementException:
				pass
			try:
				csvLine["City"] = webDriver.find_element_by_xpath("//span[@class='postingtitletext']/small").text
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

			try:
				replyButton = webDriver.find_element_by_xpath("//button[@class='reply-button js-only']")
			except:
				#For whatever reason 1 in 1000 pages just dont have a reply button?
				continue
			replyButton.click()
			time.sleep(1)

			#Craigslist is cracking down on bots so this hack resubmits
			try:
				errorElement = webDriver.find_element_by_xpath("//div[@class='lbcontent']")
				if "An error has occurred" in errorElement.text:
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

		for value in csvLine.values():
			outputFile.write(value+',')
		outputFile.write("\n")

		duplicateCatches.write("Duplicate title: " + csvLine["Full Title"]) if csvLine["Full Title"] in titleSet else titleSet.add(csvLine["Full Title"])
		duplicateCatches.write("Duplicate Address: " + csvLine["Address"]) if csvLine["Address"] in addressSet else addressSet.add(csvLine["Address"])
		bedPathPriceTuple = (csvLine["Bedrooms"], csvLine["Bathrooms"], csvLine["Price"])
		duplicateCatches.write("Duplicate bedPathPriceTuple: " + str(bedPathPriceTuple)) if bedPathPriceTuple in bedBathPriceSet else bedBathPriceSet.add(bedPathPriceTuple)
		duplicateCatches.write("Duplicate email: " + csvLine["email"]) if csvLine["email"] in emailSet else emailSet.add(csvLine["email"])
		duplicateCatches.write("Duplicate title: " + csvLine["PhoneNumber"]) if csvLine["PhoneNumber"] in phoneSet else phoneSet.add(csvLine["PhoneNumber"])

	webDriver.close()

failedURLs = open("failedListings.txt", 'w', encoding='utf-8')
outputFile = open("listings.csv", 'w', encoding='utf-8')
duplicateCatches = open("duplicates.txt", 'w', encoding='utf-8')

csvLineBlank = {"Status":"", "Full Title":"", "URL":"", "Bedrooms":"", "Bathrooms":"", "Price":"", "SqF":"","City":"", "Address":"", "PhoneNumber":"", "email":""}

# Write the first line of the file
for entry in csvLineBlank:
	outputFile.write(entry+",")
outputFile.write("\n")


url = "https://chicago.craigslist.org/search/apa"
webScrappingFutures = []
pageCount = 0
pagesToGather = 30
maxThreads = 2

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
duplicateCatches.close()

print("wrote the file")