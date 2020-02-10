# -*- coding: utf-8 -*-
import scrapy
import re
from beeradvocate.items import BeeradvocateItem


class SudsbugSpider(scrapy.Spider):
    name = 'sudsbug'
    allowed_domains = ['beeradvocate.com']
    start_urls = ['https://www.beeradvocate.com/place/directory/?show=all']

           
# Initial log in to access countries, be sure to create a beeradvocate account and replace login and password with your info
    def parse(self, response):
        self.log('\n\n\n Logging in... \n\n\n')
        return scrapy.FormRequest.from_response(response, formdata={'login': 'REPLACE_WITH_YOUR_USERNAME', 
                                                                    'register' : '0', 
                                                                    'password': 'REPLACE_WITH_YOUR_PASSWORD', 
                                                                    'cookie_check' : '1', 
                                                                    'redirect' : 'https://www.beeradvocate.com/place/directory/?show=all'}, 
                                                                    callback=self.parse_countries) 


# Simply takes all the hrefs from each country's link and passes them
    def parse_countries(self, response):
        self.log('\n\n\n Success! \n\n\n')
        country_urls= response.xpath('//tr//li/a/@href').extract()
        for url in ['https://www.beeradvocate.com{}'.format(x) for x in country_urls]:
            yield scrapy.Request(url=url, callback=self.parse_countryPage)


# United States, Canada, and the UK all have child pages including states/provinces.  Each of these children are formatted identically to other
# country pages, so accessing those child pages for those three countries and running them back through the function (i.e. "Alabama" does not satisfy
# the if statement) gets us all needed detail pages.

#We ultimately want to pass the URL from clicking on the brewery link. Thankfully, the text therein provides us with the number of breweries. There will be 20 breweries
#displayed per page in the next function, and so we can generate the URLs now based on the total number of breweries. 
    def parse_countryPage(self, response):
        countryname = str(response.xpath('//div[@class="titleBar"]/h1/text()').extract_first())
        if countryname in ['United States', 'United Kingdom', 'Canada']:
            state_urls = response.xpath('//table[1]//table[1]//a/@href').extract()
            for url in ['https://www.beeradvocate.com{}'.format(x) for x in state_urls]:
                yield scrapy.Request(url = url, callback=self.parse_countryPage)
        else: 
            brewery_num_raw = response.xpath('//table[1]//table[1]//td[1]//li[1]//text()').extract_first()
            brewery_num = int(re.findall('\d+', brewery_num_raw)[0])
            brewery_url = response.xpath('//table[1]//table[1]//td[1]//li[1]//a/@href').extract_first()
            brewery_url = ('https://www.beeradvocate.com' + brewery_url)
            if brewery_num == 0:
                return
            elif brewery_num < 21:
                yield scrapy.Request(url = brewery_url, callback = self.parse_breweryPage)
            else:
                brewery_url_splits = brewery_url.split('?')
                brewery_urls = [brewery_url_splits[0] + '?start={}&'.format(x) + brewery_url_splits[1] for x in range(0, (brewery_num + 1), 20)]
                for url in brewery_urls:
                    yield scrapy.Request(url = url, callback=self.parse_breweryPage)

#This guy just grabs the brewery URL for each brewery displayed on the search page.
    def parse_breweryPage(self, response):
        brewery_detail_urls = response.xpath('//td[@colspan =2]/a/@href').extract()
        for url in ['https://www.beeradvocate.com{}'.format(x) for x in brewery_detail_urls]:
            yield scrapy.Request(url = url, callback=self.parse_breweryDetails)

#This guy grabs every specific beer URL from the brewery detail page.
    def parse_breweryDetails(self, response):
        beer_urls = response.xpath('//td/a[contains(@href, "/beer/profile")]/@href').extract()
        for url in ['https://www.beeradvocate.com{}'.format(x) for x in beer_urls]:
            yield scrapy.Request(url = url, callback=self.parse_beers)

    def parse_beers(self, response):
        name = response.xpath('//*[@id="content"]/div/div/div[2]/div/div/div[1]/h1/text()').extract_first()
        style = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[1]/a[1]/b/text()').extract_first()
        brewery_name = response.xpath('//*[@id="content"]/div/div/div[2]/div/div/div[1]/h1/span/text()').extract_first()
        try: 
            style_rank = str(response.xpath('//*[@id="info_box"]/div[2]/dl/dd[1]/a[2]/text()').extract())
            style_rank = re.findall('\d+', style_rank)
            style_rank = int("".join(map(str, style_rank)))
        except:
            style_rank = ''
        try:
            overall_rank = str(response.xpath('//*[@id="info_box"]/div[2]/dl/dd[3]/a/text()').extract())
            overall_rank = re.findall('\d+', overall_rank)
            overall_rank = int("".join(map(str, overall_rank)))
        except:
            overall_rank = ''
        score = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[3]/span/b/text()').extract_first()
        abv = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[2]/span/b/text()').extract_first()
        avg_rating = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[4]/b/span/text()').extract_first()
        num_reviews = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[5]/span/text()').extract_first()
        num_ratings = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[6]/span/text()').extract_first()
        region = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[8]/a[1]/text()').extract_first()
        country = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[8]/a[2]/text()').extract_first()
        availability = response.xpath('//*[@id="info_box"]/div[2]/dl/dd[9]/span/text()').extract_first()


        item = BeeradvocateItem()
        item['name'] = name
        item ['style'] = style
        item['brewery'] = brewery_name
        item['score'] = score
        item['style_rank'] = style_rank
        item['overall_rank'] = overall_rank
        item['abv'] = abv
        item['avg_rating'] = avg_rating
        item['num_reviews'] = num_reviews
        item['num_ratings'] = num_ratings
        item['region'] = region
        item['country'] = country
        item['availability'] = availability

        yield item

        



                                         
