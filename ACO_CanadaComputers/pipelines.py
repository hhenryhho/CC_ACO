# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from time import time, sleep
import pymongo
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
from twisted.internet import threads, reactor
from ACO_CanadaComputers.utils.discord import Discord
from ACO_CanadaComputers.utils.autocheckout import ACOBOT

# Save or update product in mongo database
class MongoSavePipeline(object):

    mongo_collection = "products"

    def __init__(self):
        self.settings = get_project_settings()
        self.server = self.settings.get('MONGO_SERVER')
        self.port = self.settings.get('MONGO_PORT')
        self.startTime = time()

    def open_spider(self, spider):
        try:
            self.client = pymongo.MongoClient(host='{}:{}'.format(self.server, self.port), serverSelectionTimeoutMS=1)
            self.db = self.client[self.settings.get('MONGO_DB')]
            self.collection = self.db[self.mongo_collection]
        except Exception as err:
            print(err)

    def close_spider(self, spider):
        print(f'Finished scanning for restocks, took {time() - self.startTime}')
        self.client.close()

    def process_item(self, item, spider):

        
        
        name = item['name']
        
        product = self.collection.find_one({'name': name})

        # If product already in database
        if product is not None:
            # Check if the object's stock are different
            if product['stock'] != item['stock']:  
                print(product['name'], 'has changed') 
                try:
                    bot = Discord()
                    checkoutBot = ACOBOT()
                    reactor.callInThread(checkoutBot.checkout, item)
                    reactor.callInThread(bot.post, item)
                    self.collection.replace_one({'name': name}, dict(item))
                except:
                    print('Something went wrong here')
            else:
                pass
                # print('Nothing changed for: ', product['name'])

        # Product not in database, so add it in
        else:
            print('Inserting {} into database'.format(item['name']))
            self.collection.insert_one(dict(item))
        return item