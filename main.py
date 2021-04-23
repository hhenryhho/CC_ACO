from ACO_CanadaComputers.utils.login_service import CustomerLogin
from ACO_CanadaComputers.utils.captcha_service import Captcha

from twisted.internet import reactor, threads
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import json
from time import sleep, time


class Main:
    def __init__(self):
        # A class to run multiple scrapy crawlers in a process simultaneously
        self.process = CrawlerProcess(settings=get_project_settings())

        # Start captcha service
        self.captchaSolver = Captcha()

        print("Starting script")

    # Infinite blocking call in main thread
    def crawl(self):
        d = self.process.crawl("CC_Spider")
        d.addBoth(self.crawl_callback)

    def crawl_callback(self, error):
        self.crawl()

    # -----------------------------Helper Util--------------------------------------------------
    def loginUser(self):
        with open("resources/customerlist.json", "r") as customerlist:
            customers = json.load(customerlist)

        updatedCustomerList = {}

        # Get SID for each customer
        for identifier, customerData in zip(customers.keys(), customers.values()):

            # If the customer has not checked out yet
            if not customerData["checkout"]:

                email = customerData["email"]
                password = customerData["password"]

                # Find the loginObject that has a matching email
                loginItem = CustomerLogin(email, password)

                # Get the new SID and assign it to the customer
                customerData["sid"] = loginItem.getSID()

                # Add the customer to the updated customer List
                updatedCustomerList[identifier] = customerData

        with open("resources/customerlist.json", "w") as updatedFile:

            # Update the customer list
            json.dump(updatedCustomerList, updatedFile, ensure_ascii=False)

    def storeHCaptcha(self):
        captcha_start = time()

        # Removing expired HCaptcha tokens
        with open("resources/captchas.txt", "r") as captchafile:
            captchaList = [
                captcha.strip().split(",") for captcha in captchafile.readlines()
            ]
            newCaptchaList = [
                f"{captchaData[0]},{captchaData[1]}\n"
                for captchaData in captchaList
                if time() - float(captchaData[0]) < 80
            ]

        with open("resources/captchas.txt", "w") as newcaptchafile:
            for captcha in newCaptchaList:
                newcaptchafile.write(captcha)

        # Starting call to captcha service
        response = self.captchaSolver.getHCaptcha(
            "e319ba4186699ecf4b6908f994eb359a",
            "8c7a977b-4cda-4707-99fd-585679318371",
            "https://www.canadacomputers.com",
        )
        with open("resources/captchas.txt", "a") as captchafile:
            captchafile.write(f"{time()},{response}\n")
        print(f"Obtained HCaptcha Token! Took {time() - captcha_start}")

        # Removing expired HCaptcha tokens
        with open("resources/captchas.txt", "r") as captchafile:
            captchaList = [
                captcha.strip().split(",") for captcha in captchafile.readlines()
            ]
            newCaptchaList = [
                f"{captchaData[0]},{captchaData[1]}\n"
                for captchaData in captchaList
                if time() - float(captchaData[0]) < 80
            ]

        with open("resources/captchas.txt", "w") as newcaptchafile:
            for captcha in newCaptchaList:
                newcaptchafile.write(captcha)

        # Also, clear the cache in currentcheckouts
        open("resources/currentcheckouts.txt", "w").close()

    # -----------------------------Helper Util--------------------------------------------------

    # -----------------------------Twisted Calls------------------------------------------------
    def startLoginService(self):
        d = threads.deferToThread(self.loginUser)
        d.addBoth(self.login_callback)

    def login_callback(self, error):
        reactor.callLater(900, self.startLoginService)

    def startCaptchaService(self):
        d = threads.deferToThread(self.storeHCaptcha)
        d.addBoth(self.captcha_callback)

    def captcha_callback(self, error):
        reactor.callLater(15, self.startCaptchaService)

    # -----------------------------Twisted Calls------------------------------------------------


from ACO_CanadaComputers.utils.autocheckout import ACOBOT
from ACO_CanadaComputers.items import CC_Product
from ACO_CanadaComputers.utils.customer import Customer
from ACO_CanadaComputers.utils.discord import Discord

if __name__ == "__main__":
    # bot = Main()
    # # bot.startLoginService()
    # # bot.startCaptchaService()

    # # Set up the initial services first before tracking
    # reactor.callLater(1, bot.crawl)

    # reactor.run()

    bot = Discord()
    item = CC_Product()

    item["name"] = "EVGA GeForce RTX 3070 FTW3 ULTRA GAMING 8GB GDDR6 1815 MHz Boost "
    item[
        "img"
    ] = "https://ccimg.canadacomputers.com/Products/505x505/230/522/183498/20944.jpg"
    item["item_id"] = 183498
    item["stock"] = []
    bot.post(item)

    # item = CC_Product()
    # item["name"] = "GIGABYTE AORUS GeForce RTX 3060 Ti MASTER"
    # item[
    #     "img"
    # ] = "https://ccimg.canadacomputers.com/Products/500x500/230/522/156968/24988.jpg"
    # item["item_id"] = 184167
    # item["stock"] = [{"Marché Central": 1}]

    # customer = Customer(
    #     "Henry",
    #     "Ho",
    #     "647",
    #     "713",
    #     "4507",
    #     "henryho73@hotmail.com",
    #     "Smokey100",
    #     "1234",
    #     "Ho",
    #     [
    #         "Downtown Toronto",
    #         "Midtown Toronto",
    #         "North York",
    #         "Scarborough",
    #         "Richmond Hill",
    #         "Etobicoke",
    #         "Mississauga",
    #         "Brampton",
    #         "Burlington",
    #         "Oakville",
    #         "Hamilton",
    #         "Markham",
    #         "Ajax",
    #         "Barrie",
    #         "Newmarket",
    #         "Whitby",
    #         "Oshawa",
    #         "Vaughan",
    #         "Marché Central",
    #     ],
    #     "8e6ktdd5uv3jplnrrgkj92unl6",
    #     ["3060 Ti", "3070", "3090"],
    # )

    # bot = ACOBOT()
    # reactor.callInThread(bot.checkout, customer, item)

    # customer = Customer(
    #     "Mohona",
    #     "Syed",
    #     "647",
    #     "713",
    #     "4507",
    #     "mohona.syed@gmail.com",
    #     "Smokey100",
    #     "1234",
    #     "Syed",
    #     [
    #         "Downtown Toronto",
    #         "Midtown Toronto",
    #         "North York",
    #         "Scarborough",
    #         "Richmond Hill",
    #         "Etobicoke",
    #         "Mississauga",
    #         "Brampton",
    #         "Burlington",
    #         "Oakville",
    #         "Hamilton",
    #         "Markham",
    #         "Ajax",
    #         "Barrie",
    #         "Newmarket",
    #         "Whitby",
    #         "Oshawa",
    #         "Vaughan",
    #     ],
    #     "8e6ktdd5uv3jplnrrgkj92unl6",
    #     ["3060 Ti", "3070", "3090"],
    # )
    # reactor.callLater(2, bot.checkout, customer, item)

    # reactor.run()