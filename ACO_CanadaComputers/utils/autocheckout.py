import json
from time import time
import requests
from ACO_CanadaComputers.utils.customer import Customer
from ACO_CanadaComputers.utils.login_service import CustomerLogin

class ACOBOT():

    def __init__(self): 
        print('Starting auto checkout')

    def checkout(self, item):
        customers = self.getCustomers()

        for customer in customers:

            # Get the customer's preferred items
            preferredLocations = customer.locations
            preferredGPUS = customer.gpus

            for stock in item['stock']:
                location = list(stock.keys())[0]
                quantity = list(stock.values())[0]

                # If the item that restocked matches the current customer's preferences
                if quantity > 0 and location in preferredLocations and any(gpu in item['name'] for gpu in preferredGPUS): 

                    # Start up the script to check out
                    success = self.start_cart(customer, item, self.encodeLocation(location))

                    # Only execute for the first customer
                    return success

    def encodeLocation(self, location):
        with open('resources/locationcodes.txt', 'r', encoding='utf-8') as locationFile:
            locations = [locationData.strip().split(',') for locationData in locationFile.readlines()]
        return [locationPairing[1] for locationPairing in locations if locationPairing[0] == location][0]

    # Return a customer object
    def getCustomers(self):

        with open('resources/customerlist.json', 'r') as customerlist:
            customers = json.load(customerlist)

        for _, customer in zip(customers.keys(), customers.values()):
            if not customer['checkout']:
                yield Customer(
                    firstname = customer['firstname'], 
                    lastname = customer['lastname'],
                    areacode = customer['areacode'],
                    three = customer['three'],
                    four = customer['four'],
                    email = customer['email'],
                    password = customer['password'],
                    carddigits = customer['carddigits'],
                    cardname = customer['cardname'],
                    locations = customer['locations'],
                    gpus = customer['gpus'],
                    sid = customer['sid'],
                    )

    # Return a HCaptcha token from a file in the form of a string
    def getValidCaptcha(self):

        with open('resources/captchas.txt', 'r') as captchafile:
            captchaList = [captcha.strip().split(',') for captcha in captchafile.readlines()]

        validToken = ''

        while captchaList:
            captchaToBeRemoved = captchaList.pop(0)
            if time() - float(captchaToBeRemoved[0]) < 70:
                validToken = captchaToBeRemoved[1]
                break
            
        updatedCaptchaList = [f'{captchaData[0]},{captchaData[1]}\n' for captchaData in captchaList]

        with open('resources/captchas.txt', 'w') as newcaptchafile:
            for captcha in updatedCaptchaList:
                newcaptchafile.write(captcha)  
        
        return validToken
        
    def start_cart(self, customer, item, location):

        success = False

        cookies = {
            'sid': customer.sid
        }

        start_time = time()
        print("------ Starting AutoCheckout Script ------")
        # ------------------------Add To Cart--------------------------------------------------------------------
        headersATC = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.canadacomputers.com/',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        paramsATC = (
            ('action', 'buy_now'),
            ('item_id', item['item_id']),
            ('limit', '0'),
        )
        try: 
            AddToCart = requests.get('https://www.canadacomputers.com/index.php', headers=headersATC, params=paramsATC, cookies=cookies, timeout=0.5)
            print('Added to cart')
        except requests.exceptions.ReadTimeout:
            print('Skipped waiting to finish adding to cart')
        # ------------------------------------------------------------------------------------------------------

        # ------------------------Shipping----------------------------------------------------------------------
        headersShipping = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://www.canadacomputers.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.canadacomputers.com/?checkout-shipping',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        dataShipping = {
        'ch-method': 'pickup',
        'ch-shiptoanother-firstname': customer.firstname,
        'ch-shiptoanother-lastname': customer.lastname,
        'ch-shiptoanother-company': '',
        'ch-shiptoanother-address': '',
        'ch-shiptoanother-suburb': '',
        'ch-shiptoanother-city': '',
        'ch-shiptoanother-prov-drpdn': '',
        'ch-shiptoanother-country': 'Canada',
        'ch-shiptoanother-postal': '',
        'ch-depot': location,
        'checkout_shipping': ''
        }
        shippingCheckpoint = requests.get('https://www.canadacomputers.com/checkout_shipping.php', headers=headersShipping, cookies=cookies)
        shipping = requests.post('https://www.canadacomputers.com/checkout_shipping.php', headers=headersShipping, cookies=cookies, data=dataShipping)
        file = open("ACO_CanadaComputers/utils/proofs/shipping.html", "w")
        file.write(shipping.text)
        if 'Payment Information' in shipping.text:
            print('Added shipping info')
        else:
            print('Failed adding shipping information')
        # -----------------------------------------------------------------------------------------------------

        # --------------------------Payment--------------------------------------------------------------------
        headersPayment = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://www.canadacomputers.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.canadacomputers.com/?checkout-payment',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        dataPayment = {
        'ch-methodofpayment': 'pay_instore',
        'ch-frm-flexiticard-number': '',
        'ch-frm-paymentcontact-areacode': customer.areacode,
        'ch-frm-paymentcontact-phone-three': customer.three,
        'ch-frm-paymentcontact-phone-four': customer.four,
        'ch-frm-paymentcontact-ext': '',
        'ch-frm-paymentcontact-email': customer.email,
        'ch-frm-paymentcontact-card-number': customer.carddigits,
        'ch-frm-paymentcontact-card-holder': customer.cardname,
        'checkout_payment': ''
        }

        payment = requests.post('https://www.canadacomputers.com/checkout_payment.php', headers=headersPayment, cookies=cookies, data=dataPayment)
        file = open("ACO_CanadaComputers/utils/proofs/payment.html", "w")
        file.write(payment.text)
        if 'Customer Information' in payment.text:
            print('Added payment info')
        else: 
            print('Failed adding payment information')
        # -------------------------------------------------------------------------------------------------------

        # --------------------------Check Out--------------------------------------------------------------------
        headersConfirmation = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://www.canadacomputers.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.canadacomputers.com/?checkout-confirmation',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        dataConfirmation = {
        'ch_shippingtnc': 'agree',
        'h-captcha-response': self.getValidCaptcha(),
        'checkout_confirmation': ''
        }

        confirmation = requests.post('https://www.canadacomputers.com/checkout_confirmation.php', headers=headersConfirmation, cookies=cookies, data=dataConfirmation)
        file = open("ACO_CanadaComputers/utils/proofs/confirmation.html", "w")
        file.write(confirmation.text)
        if 'Order Number' in confirmation.text:
            success = True
            print('Checked out!')
        else:
            print('Failed check out')
        # --------------------------------------------------------------------------------------------------------
        print("--- %s seconds ---" % (time() - start_time))
        # --------------------------Remove from cart after success------------------------------------------------
        headersPostSuccess = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'Referer': 'https://www.canadacomputers.com/?checkout-confirmation',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = requests.get('https://www.canadacomputers.com/checkout_success.php', headers=headersPostSuccess, cookies=cookies)
        # ---------------------------------------------------------------------------------------------------------

        return success

if __name__ == "__main__":
    bot = ACOBOT()
    bot.getValidCaptcha()

