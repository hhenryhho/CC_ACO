import json
from time import time
import requests


class ACOBOT:
    def __init__(self):
        proxy = {
            "http": "http://vujrudun-dest:a5qpz8fuhjkt@23.236.170.227:9260/",
            "https": "http://vujrudun-dest:a5qpz8fuhjkt@23.236.170.227:9260/",
        }
        self.s = requests.Session()
        self.s.proxies.update(proxy)
        print("Starting auto checkout")

    def checkout(self, customer, item):
        with open("resources/currentcheckouts.txt", "r") as currentcustomersFile:
            currentcustomers = [
                customers.strip() for customers in currentcustomersFile.readlines()
            ]

        # If the customer is not currently being checked out, then add him in
        if not any(
            currentcustomer == customer.email for currentcustomer in currentcustomers
        ):

            # Append this customer to the end
            with open("resources/currentcheckouts.txt", "a") as currentcustomersFile:
                currentcustomersFile.write(customer.email + "\n")
                print("Wrote customer")

            # Make sure the location matches the preferences
            for stock in item["stock"]:
                for location, quantity in zip(stock.keys(), stock.values()):
                    if quantity != 0 and location in customer.locations:
                        # Start up the script to check out
                        print(customer)
                        print(item["item_id"])
                        print(self.encodeLocation(location))
                        self.start_cart(
                            customer, item["item_id"], self.encodeLocation(location)
                        )

        else:
            print(f"{customer.firstname} already checked out")

    """
    Encode the specified location into its letter code
    """

    def encodeLocation(self, location):
        with open("resources/locationcodes.txt", "r", encoding="utf-8") as locationFile:
            locations = [
                locationData.strip().split(",")
                for locationData in locationFile.readlines()
            ]
        return [
            locationPairing[1]
            for locationPairing in locations
            if locationPairing[0] == location
        ][0]

    """ 
    Return a HCaptcha token from a file in the form of a string
    """

    def getValidCaptcha(self):

        with open("resources/captchas.txt", "r") as captchafile:
            captchaList = [
                captcha.strip().split(",") for captcha in captchafile.readlines()
            ]

        validToken = ""

        while captchaList:
            captchaToBeRemoved = captchaList.pop(0)
            if time() - float(captchaToBeRemoved[0]) < 70:
                validToken = captchaToBeRemoved[1]
                break

        updatedCaptchaList = [
            f"{captchaData[0]},{captchaData[1]}\n" for captchaData in captchaList
        ]

        with open("resources/captchas.txt", "w") as newcaptchafile:
            for captcha in updatedCaptchaList:
                newcaptchafile.write(captcha)

        return validToken

    """
    Takes a customer, and tries to checkout the specified item at the specified location
    """

    def start_cart(self, customer, item_id, location):

        success = False

        cookies = {"sid": customer.sid}

        start_time = time()
        print("------ Starting AutoCheckout Script ------")
        # ------------------------Add To Cart--------------------------------------------------------------------
        headersATC = {
            "Connection": "keep-alive",
            "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.canadacomputers.com/",
            "Accept-Language": "en-US,en;q=0.9",
        }

        paramsATC = (
            ("action", "buy_now"),
            ("item_id", item_id),
            ("limit", "0"),
        )
        try:
            AddToCart = self.s.get(
                "https://www.canadacomputers.com/index.php",
                headers=headersATC,
                params=paramsATC,
                cookies=cookies,
                timeout=0.5,
            )
            print("Added to cart")
        except requests.exceptions.ReadTimeout:
            print("Skipped waiting to finish adding to cart")
        # ------------------------------------------------------------------------------------------------------

        # ------------------------Shipping----------------------------------------------------------------------
        headersShipping = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://www.canadacomputers.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.canadacomputers.com/?checkout-shipping",
            "Accept-Language": "en-US,en;q=0.9",
        }

        dataShipping = {
            "ch-method": "pickup",
            "ch-shiptoanother-firstname": customer.firstname,
            "ch-shiptoanother-lastname": customer.lastname,
            "ch-shiptoanother-company": "",
            "ch-shiptoanother-address": "",
            "ch-shiptoanother-suburb": "",
            "ch-shiptoanother-city": "",
            "ch-shiptoanother-prov-drpdn": "",
            "ch-shiptoanother-country": "Canada",
            "ch-shiptoanother-postal": "",
            "ch-depot": location,
            "checkout_shipping": "",
        }
        # You need to go inside the cart before doing anything else

        shippingCheckpoint = self.s.get(
            "https://www.canadacomputers.com/checkout_shipping.php",
            headers=headersShipping,
            cookies=cookies,
        )

        shipping = self.s.post(
            "https://www.canadacomputers.com/checkout_shipping.php",
            headers=headersShipping,
            cookies=cookies,
            data=dataShipping,
        )
        file = open(
            f"ACO_CanadaComputers/utils/proofs/checkouts/{customer.email}-shipping.html",
            "w",
        )
        file.write(shipping.text)
        if "Payment Information" in shipping.text:
            print("Added shipping info")
        else:
            print("Failed adding shipping information")
        # -----------------------------------------------------------------------------------------------------

        # --------------------------Payment--------------------------------------------------------------------
        headersPayment = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://www.canadacomputers.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.canadacomputers.com/?checkout-payment",
            "Accept-Language": "en-US,en;q=0.9",
        }

        dataPayment = {
            "ch-methodofpayment": "pay_instore",
            "ch-frm-flexiticard-number": "",
            "ch-frm-paymentcontact-areacode": customer.areacode,
            "ch-frm-paymentcontact-phone-three": customer.three,
            "ch-frm-paymentcontact-phone-four": customer.four,
            "ch-frm-paymentcontact-ext": "",
            "ch-frm-paymentcontact-email": customer.email,
            "ch-frm-paymentcontact-card-number": customer.carddigits,
            "ch-frm-paymentcontact-card-holder": customer.cardname,
            "checkout_payment": "",
        }

        payment = self.s.post(
            "https://www.canadacomputers.com/checkout_payment.php",
            headers=headersPayment,
            cookies=cookies,
            data=dataPayment,
        )
        file = open(
            f"ACO_CanadaComputers/utils/proofs/checkouts/{customer.email}-payment.html",
            "w",
        )
        file.write(payment.text)
        if "Customer Information" in payment.text:
            print("Added payment info")
        else:
            print("Failed adding payment information")
        # -------------------------------------------------------------------------------------------------------

        # --------------------------Check Out--------------------------------------------------------------------
        headersConfirmation = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://www.canadacomputers.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.canadacomputers.com/?checkout-confirmation",
            "Accept-Language": "en-US,en;q=0.9",
        }

        dataConfirmation = {
            "ch_shippingtnc": "agree",
            "h-captcha-response": self.getValidCaptcha(),
            "checkout_confirmation": "",
        }

        confirmation = self.s.post(
            "https://www.canadacomputers.com/checkout_confirmation.php",
            headers=headersConfirmation,
            cookies=cookies,
            data=dataConfirmation,
        )
        file = open(
            f"ACO_CanadaComputers/utils/proofs/checkouts/{customer.email}-confirmation.html",
            "w",
        )
        file.write(confirmation.text)
        if "Grand Total" in confirmation.text:
            try:
                self.updatedSuccess(customer)
            except Exception as err:
                print(f"Couldnt update checkout status due to: {err}")
            success = True
            print("Checked out!")
        else:
            print("Failed check out")
        # --------------------------------------------------------------------------------------------------------
        print("----- %s seconds -----" % (time() - start_time))
        # --------------------------Remove from cart after success------------------------------------------------
        headersPostSuccess = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "Referer": "https://www.canadacomputers.com/?checkout-confirmation",
            "Accept-Language": "en-US,en;q=0.9",
        }

        cleared = self.s.get(
            "https://www.canadacomputers.com/checkout_success.php",
            headers=headersPostSuccess,
            cookies=cookies,
        )
        file = open(
            f"ACO_CanadaComputers/utils/proofs/checkouts/{customer.email}-cleared.html",
            "w",
        )
        file.write(cleared.text)
        # ---------------------------------------------------------------------------------------------------------

        return success

    """
    Update the checkout status of the user with true if succeeded
    """

    def updatedSuccess(self, customer):
        updatedCustomerList = {}
        removedCustomerList = {}

        with open("resources/customerlist.json", "r") as customerlist:
            customers = json.load(customerlist)

        # Get SID for each customer
        for identifier, customerData in zip(customers.keys(), customers.values()):

            # If the customer is the current customer that checked out
            if customer.email == customerData["email"]:

                # Update their checkout info to true
                customerData["checkout"] = True

                # Move him to the removed customer list
                removedCustomerList[identifier] = customerData

            else:

                # Add the customer to the list
                updatedCustomerList[identifier] = customerData

        with open("resources/customerlist.json", "w") as updatedFile, open(
            "resources/removedcustomerlist.json", "a"
        ) as removedFile:

            # Update the customer list
            json.dump(updatedCustomerList, updatedFile, ensure_ascii=False)

            if removedCustomerList:

                # Update the removed list
                json.dump(removedCustomerList, removedFile, ensure_ascii=False)


if __name__ == "__main__":
    bot = ACOBOT()
    bot.getValidCaptcha()
