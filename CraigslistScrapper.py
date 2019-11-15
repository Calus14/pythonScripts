import urllib.request
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

#Method that takes a given URL and returns a list of strings seperated by newline
def getUrlsStrings(url="https://chicago.craigslist.org/search/apa"):
	fp = urllib.request.urlopen(url)
	urlBytes = fp.read()
	fp.close()
	
	return urlBytes.decode("utf8").split( '\n')

#Method that takes a list of strings that represents a valid html object and returns
#a list of strings for the all given sections that matches element the given type, id and or class
def getHtmlSectionStrings(htmlStrings, elementType, className=None, idName=None):
	
	listOfSubSections = []
	subSectionStrings = []
	#Specific tag were looking for
	specificTagFoundTag = False
	#Stack count because we can have similar element types as sub-children
	elementTypeTagCount = 0
	
	for s in htmlStrings:
	
		#If we havent found the specific tag yet this might be the starting of the section
		if not specificTagFoundTag and stringMatchesTags(s, elementType, className, idName):
			specificTagFoundTag = True
		
		#If this line isnt the start and we still havent found it then we are out of the section
		if not specificTagFoundTag:
			continue
			
		subSectionStrings.append(s)
		#Check for sub element types of the same kind
		if ("<"+elementType) in s:
			elementTypeTagCount = elementTypeTagCount+1
		if ("</"+elementType+">") in s:
			elementTypeTagCount = elementTypeTagCount-1
		if elementTypeTagCount == 0:
			listOfSubSections.append(subSectionStrings)
			specificTagFoundTag = False
			
	return listOfSubSections

#helper method that tells us if the line matches the start tag
def stringMatchesTags(htmlLine, elementType, className=None, idName=None):
	return htmlLine.strip().startswith("<"+elementType) and (className == None or ("class=\""+className+"\"" in htmlLine) ) and (idName == None or ("id=\""+idName+"\"" in htmlLine) )
	
def getCraigsListURLs():
	url = "https://chicago.craigslist.org/search/apa"
	#Get all of the HTML for apartments
	urlRawStrings = getUrlsStrings(url)
	#Get just the content that holds all of the listings -DRILL DOWN
	contentHtmlStrings = getHtmlSectionStrings(urlRawStrings, "div", "content", "sortable-results")[0]
	#Get table holding the listings - DRILL DOWN
	listHtml = getHtmlSectionStrings(contentHtmlStrings, "ul", "rows")[0]
	#Get individual postings - Final Drill Down
	postingsHtml = getHtmlSectionStrings(listHtml, "li", "result-row")
	
	postingUrls = []
	

	for line in postingsHtml:
		linkHtml = getHtmlSectionStrings(line, "a", "result-image gallery")
		#each li tag has a few link sections. grab the first section of each, then grab the first attribute which is the href . 
		#first attribute will be 1 index because of the element tag
		#urlLink will be href="<what we want>"
		urlLink = linkHtml[0][0].strip().split(" ")[1].lstrip("href=").strip("\"")	
		postingUrls.append(urlLink)
		
	return postingUrls
	
webDriver = webdriver.Chrome()
outputFile = open("listings.csv", 'w', encoding='utf-8')
postUrls = getCraigsListURLs()

# Status, Bedrooms, Bathrooms, Price, SqF, Address, City/neighborhood, Contact Name, PhoneNumber, email

for url in postUrls:
	webDriver.get(url)
	#Get the page to load the email and phone number
	#replyButtons = webDriver.find_elements_by_xpath("//button[@class='reply-button']")

	replyButton = webDriver.find_elements_by_xpath("//button[@role='button']")[0]
	replyButton.click()
	
	try:
		showPhoneButton = webDriver.find_element_by_xpath("/button[@class='show-phone']")
		showPhoneButton.click()
	except NoSuchElementException: 
		print("No Phone Number")
		
	#Now we just need to get the data we need and write to our listings csv file
	email = webDriver.find_elements_by_xpath("//div/div/aside/ul/li/p[@class='reply-email-address']")
	print(email)
	for i in range(10):
		print("\n")
#	email = webDriver.find_elements_by_xpath("//div/div/aside/ul/li/p[@class='reply-email-address']")[0].text
	outputFile.write(email+"\n")	


outputFile.close()



print("wrote the file")