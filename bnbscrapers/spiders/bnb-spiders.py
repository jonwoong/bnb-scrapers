##### HEADERS #####
import time
import re
import utilities # utilities.py
from utilities import *

import scrapy # spiders
from scrapy import Spider
from scrapy.item import Item, Field

import selenium # used to load web pages
from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

chromedriver_options = webdriver.ChromeOptions()
chromedriver_options.add_argument("headless")

################################################################################
# From each listing, we scrape 
# 	property_name
# 	hosts
#	address
#	phone_number
# 	website
# 	rooms
# 	url (of bnbfinder listing)
# 	email_address 
#
# 	If these are unavailable, they are left blank
################################################################################

class Listing(Item):
	property_name = Field()
	hosts = Field()
	address = Field()
	phone_number = Field()
	website = Field()
	rooms = Field()
	url = Field()
	email_address = Field()

################################################################################
class BNBFinderSpider(Spider):
	name = "bnbfinder" # name of spider

	start_urls = ["https://www.bnbfinder.com/search-result?gmw_address%5B0%5D&gmw_post=inn&gmw_distance=60&gmw_units=imperial&gmw_form=2&gmw_per_page=" + str(SAMPLE_SIZE) + "&gmw_lat&gmw_lng&gmw_px=pt&action=gmw_post"]

	def parse(self, response):
		# When the spider reaches the page with all listings, click (or follow) each listing
		for href in response.css("a.inn-sort-title::attr(href)").extract():
			yield response.follow(href, self.parse_listing)

	# for each listing, extract relevant fields
	def parse_listing(self, response):
		listing = Listing()
		listing['property_name'] = response.css("h1::text").extract_first()
		if response.xpath('//p[contains(text(),"Host(s):")]/text()'):
			listing['hosts'] = response.xpath('//p[contains(text(),"Host(s):")]/text()').extract_first().split(": ")[1]
		listing['address'] = response.css("p::text")[0].extract().strip() + ', ' + response.css("p::text")[1].extract().strip()
		listing['phone_number'] = response.css("p::text")[2].extract()
		listing['website'] = response.xpath('//a[contains(text(),"WEBSITE")]/@href').extract_first()
		if response.xpath('//p[contains(text(),"Rooms:")]/text()'):
			listing['rooms'] = response.xpath('//p[contains(text(),"Rooms:")]/text()').extract_first().split(": ")[1].split(" ")[0]
		listing['url'] = response.url
		if response.xpath('//a[contains(text(),"E-MAIL")]/@href'):
			listing['email_address'] = decode(response.xpath('//a[contains(text(),"E-MAIL")]/@href').extract_first().split(':')[1].split('?')[0])
		yield listing

class INNKEEPERSpider(Spider):
	name = "innkeeper"

	base_url = "http://theinnkeeper.com/location/na/"
	all_url = [base_url]
	for x in range(2,305):
		all_url.append(base_url + "page/" + str(x) + "/")
	start_urls = all_url

	def parse(self, response):
		# click each listing
		for href in response.xpath('//span[@class="loopInfo more-info"]').css("a::attr(href)").extract():
			yield response.follow(href, self.parse_listing) 

	def parse_listing(self, response):
		listing = Listing()
		listing['property_name'] = response.css("h1::text").extract_first()
		listing['hosts'] = response.xpath('//ul[@class="extraInfo"]/li/text()').extract_first()
		raw_address_data = response.xpath('//div[@class="location"]/span[@class="loopInfo"]/text()').extract()
		listing['address'] = raw_address_data[0].strip() + ", " + raw_address_data[1].strip()
		listing['phone_number'] = response.xpath('//ul[@class="listingInfo"]/li/span[@class="loopInfo"]/text()').extract_first()
		listing['website'] = response.xpath('//span[@class="listing-button loopInfo"]/a/@href').extract_first()
		if response.xpath('//ul[@class="extraInfo"]/li/span/text()'):
			listing['rooms'] = response.xpath('//ul[@class="extraInfo"]/li/span/text()').extract_first()
		listing['url'] = response.url
		if response.xpath('//a[contains(text(),"Email")]/@href'):
			listing['email_address'] = response.xpath('//a[contains(text(),"Email")]/@href').extract_first().split(":")[1]
		yield listing






