from ACO_CanadaComputers.utils.login_service import CustomerLogin
from ACO_CanadaComputers.utils.captcha_service import Captcha

from twisted.internet import reactor, threads
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import json
from time import sleep, time

class Main():

    def __init__(self):
        # A class to run multiple scrapy crawlers in a process simultaneously
        self.process = CrawlerProcess(settings=get_project_settings())

        with open('resources/customerlist.json', 'r') as customerlist:
            self.customers = json.load(customerlist)

        # Start captcha service
        self.captchaSolver = Captcha()
        
        print('Starting script')

    # Infinite blocking call in main thread
    def crawl(self):
        d = self.process.crawl('CC_Spider')
        d.addBoth(self.crawl_callback)

    def crawl_callback(self, error):
        sleep(2)
        self.crawl()

    #-----------------------------Helper Util--------------------------------------------------
    def loginUser(self):

        updatedCustomerList = {}
        removedCustomerList = {}

        # Get SID for each customer
        for identifier, customerData in zip(self.customers.keys(), self.customers.values()):

            # If the customer has not checked out yet
            if not customerData['checkout']:

                email = customerData['email']
                password = customerData['password']

                # Find the loginObject that has a matching email
                loginItem = CustomerLogin(email, password)
                
                # Get the new SID and assign it to the customer
                customerData['sid'] = loginItem.getSID()
            
                # Add the customer to the updated customer List
                updatedCustomerList[identifier] = customerData
            
            else:
                
                # Add the customer to the removed customer List
                removedCustomerList[identifier] = customerData

        with open('resources/customerlist.json', 'w') as updatedFile, open('resources/removedcustomerlist.json', 'a') as removedFile:

            # Update the customer list
            json.dump(updatedCustomerList, updatedFile)
            
            # Update the removed list
            json.dump(removedCustomerList, removedFile)

    def storeHCaptcha(self):
        captcha_start = time()

        # Removing expired HCaptcha tokens
        with open('resources/captchas.txt', "r") as captchafile:
            captchaList = [captcha.strip().split(',') for captcha in captchafile.readlines()]
            newCaptchaList = [f'{captchaData[0]},{captchaData[1]}\n' for captchaData in captchaList if time() - float(captchaData[0]) < 80]

        with open('resources/captchas.txt', "w") as newcaptchafile:  
            for captcha in newCaptchaList:
                newcaptchafile.write(captcha)  

        # Starting call to captcha service
        response = self.captchaSolver.getHCaptcha('e319ba4186699ecf4b6908f994eb359a', '8c7a977b-4cda-4707-99fd-585679318371', 'https://www.canadacomputers.com')
        with open('resources/captchas.txt', "a") as captchafile:
            captchafile.write(f'{time()},{response}\n')
        print(f'Obtained HCaptcha Token! Took {time() - captcha_start}')

        # Removing expired HCaptcha tokens
        with open('resources/captchas.txt', "r") as captchafile:
            captchaList = [captcha.strip().split(',') for captcha in captchafile.readlines()]
            newCaptchaList = [f'{captchaData[0]},{captchaData[1]}\n' for captchaData in captchaList if time() - float(captchaData[0]) < 80]

        with open('resources/captchas.txt', "w") as newcaptchafile:  
            for captcha in newCaptchaList:
                newcaptchafile.write(captcha)  
    #-----------------------------Helper Util--------------------------------------------------


    #-----------------------------Twisted Calls------------------------------------------------
    def startLoginService(self):
        d = threads.deferToThread(self.loginUser)
        d.addBoth(self.login_callback)

    def login_callback(self, error):
        reactor.callLater(900, self.startLoginService)

    def startCaptchaService(self):
        d = threads.deferToThread(self.storeHCaptcha)
        d.addBoth(self.captcha_callback)

    def captcha_callback(self, error):
        reactor.callLater(5, self.startCaptchaService)
    #-----------------------------Twisted Calls------------------------------------------------

from ACO_CanadaComputers.utils.autocheckout import ACOBOT
from ACO_CanadaComputers.utils.discord import Discord
from ACO_CanadaComputers.items import CC_Product


test = 1

if __name__ == "__main__" and test == 1:
    bot = Main()
    bot.startLoginService()
    bot.startCaptchaService()
    
    # item = CC_Product()
    # item['name'] = 'MSI GeForce RTX 3070 GAMING X TRIO, 8GB GDDR6, 1830 MHZ Boost Clock, PCIe 4.0, 256-Bit, 1 x HDMI 2.1, 3 x DisplayPort 1.4a, 8-pin x2'
    # item['img'] = 'https://ccimg.canadacomputers.com/Products/600x600/230/522/183210/80413.jpg'
    # item['item_id'] = 183210
    # item['stock'] = [{'Scarborough':3}]

    # Set up the initial services first before tracking
    reactor.callLater(30, bot.crawl)

    reactor.run()
    
