# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from time import time
import json
import pymongo
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from ACO_CanadaComputers.utils.discord import Discord
from ACO_CanadaComputers.utils.autocheckout import ACOBOT
from ACO_CanadaComputers.utils.customer import Customer

# Save or update product in mongo database
class MongoSavePipeline(object):

    mongo_collection = "products"

    def __init__(self):
        self.settings = get_project_settings()
        self.server = self.settings.get("MONGO_SERVER")
        self.port = self.settings.get("MONGO_PORT")
        self.customers = list(self.getCustomerList())
        self.startTime = time()

    def open_spider(self, spider):
        try:
            self.client = pymongo.MongoClient(
                host="{}:{}".format(self.server, self.port), serverSelectionTimeoutMS=1
            )
            self.db = self.client[self.settings.get("MONGO_DB")]
            self.collection = self.db[self.mongo_collection]
        except Exception as err:
            print(err)

    def close_spider(self, spider):
        print(f"Finished scanning for restocks, took {time() - self.startTime}")
        self.client.close()

    def process_item(self, item, spider):

        name = item["name"]

        product = self.collection.find_one({"name": name})

        # If product already in database
        if product is not None:

            # Check if the object's stock are different
            if product["stock"] != item["stock"]:
                print(product["name"], "has changed")

                # -----------------------------Calls to external objects----------------
                bot = Discord()
                reactor.callInThread(bot.post, item)

                # Go through the list of customers
                for customer in self.customers:
                    # Find the first customer whose preferences matches the item description
                    print(f"Matches: {self.matchPreferences(customer, item)}")
                    if self.matchPreferences(customer, item) and item["stock"]:
                        # Remove that customer from the list
                        self.customers.remove(customer)
                        # Checkout the item
                        checkoutBot = ACOBOT()
                        reactor.callInThread(checkoutBot.checkout, customer, item)
                # -----------------------------------------------------------------------

                self.collection.replace_one({"name": name}, dict(item))
        # Product not in database, so add it in
        else:
            print("Inserting {} into database".format(item["name"]))
            self.collection.insert_one(dict(item))
        return item

    """
    Read the list of customers within the customerList.json file and returns a list of all customers as a Customer object
    """

    def getCustomerList(self):

        with open("resources/customerlist.json", "r") as customerlist:
            customers = json.load(customerlist)

        for _, customer in zip(customers.keys(), customers.values()):
            if not customer["checkout"]:
                yield Customer(
                    firstname=customer["firstname"],
                    lastname=customer["lastname"],
                    areacode=customer["areacode"],
                    three=customer["three"],
                    four=customer["four"],
                    email=customer["email"],
                    password=customer["password"],
                    carddigits=customer["carddigits"],
                    cardname=customer["cardname"],
                    locations=customer["locations"],
                    sid=customer["sid"],
                    gpus=customer["gpus"],
                )

    def matchPreferences(self, customer, item):

        # Get the customer's preferred items
        preferredLocations = customer.locations
        preferredGPUS = customer.gpus

        for stock in item["stock"]:
            location = list(stock.keys())[0]
            quantity = list(stock.values())[0]

            # If the item that restocked matches the current customer's preferences
            if (
                quantity != 0
                and location in preferredLocations
                and any(gpu in item["name"] for gpu in preferredGPUS)
            ):
                return True

        return False