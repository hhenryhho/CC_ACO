
import scrapy
import random
from ACO_CanadaComputers.items import CC_Product

class CCSpider(scrapy.Spider):

    name = 'CC_Spider'

    def __init__(self):
        with open('useragents.txt', 'r') as useragentlist:
            self.useragents = [url.strip() for url in useragentlist.readlines()]

    def start_requests(self): 
        start_urls = [
            'https://www.canadacomputers.com/index.php?cPath=43_557_559&sf=:3_3,3_5,3_7,3_8,3_9&mfr=&pr=&ajax=true&page=1',
            'https://www.canadacomputers.com/index.php?cPath=43_557_559&sf=:3_3,3_5,3_7,3_8,3_9&mfr=&pr=&ajax=true&page=2',
            'https://www.canadacomputers.com/index.php?cPath=43_557_559&sf=:3_3,3_5,3_7,3_8,3_9&mfr=&pr=&ajax=true&page=3',
            'https://www.canadacomputers.com/index.php?cPath=43_557_559&sf=:3_3,3_5,3_7,3_8,3_9&mfr=&pr=&ajax=true&page=4',
            'https://www.canadacomputers.com/index.php?cPath=43_557_559&sf=:3_3,3_5,3_7,3_8,3_9&mfr=&pr=&ajax=true&page=5',
            'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_20,3_31&mfr=&pr=&ajax=true&page=1',
            'https://www.canadacomputers.com/index.php?cPath=43_557&sf=:3_20,3_31&mfr=&pr=&ajax=true&page=2'
        ]
        for url in start_urls:
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "host": "www.canadacomputers.com",
                "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent":random.choice(self.useragents)
            }
            yield scrapy.Request(url, headers=headers, dont_filter=True)

    def parse(self, response):

        # Get the list of products (first stock levels, then product template)
        productlist = response.xpath('/html/body/div')

        for stockinfo, productinfo in zip(productlist[0::2], productlist[1::2]):
            
            # --------------------START OF GET PRODUCT INFO -------------------------
            # productURL = productinfo.css('a.text-dark::attr(href)').get()
            productName = productinfo.css('a.text-dark::text').get()
            productIMG = productinfo.css('img::attr(src)').get().replace('105x105','500x500')
            productID = productinfo.css('div.productTemplate::attr(data-item-id)').get()
            # --------------------END OF GET PRODUCT INFO --------------------------


            # --------------------START OF GET STOCK QUANTITY AND LOCATION ----------
            # Keeps track of stock over different locations
            stock = []

            # Get the list of provinces
            provinces = stockinfo.css('div.col-border-bottom')

            # Go through each province
            for province in provinces:

                # Get the list of stores within the province
                storelist = province.css('div.col-md-4')

                # Go through each store
                for store in storelist:
                    
                    # GET LOCATION
                    if store.css('p').css('a::text').get() == None:
                        location = store.css('p::text').get()
                    elif store.css('p').css('a::text').get().strip() != '':
                        location = store.css('p').css('a::text').get()

                    # GET STOCK
                    if store.css('span.stocknumber::text').get() != None:
                        quantity = store.css('span.stocknumber::text').get()
                    else:
                        quantity = 0

                    if location.strip() == 'St. Catharines':
                        stock.append({'St Catharines':quantity})
                    elif location.strip() != '':   
                        stock.append({location.strip():quantity})
            # --------------------END OF GET STOCK QUANTITY AND LOCATION ------------

            # --------------------START OF SEND THE ITEM TO THE PIPELINE ------------
            product = CC_Product()
            product['name'] = productName
            product['img'] = productIMG
            product['item_id'] = productID
            product['stock'] = stock

            yield product
            # --------------------END OF SEND THE ITEM TO THE PIPELINE --------------