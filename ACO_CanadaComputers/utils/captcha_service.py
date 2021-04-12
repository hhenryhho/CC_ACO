from capmonster_python import HCaptchaTaskProxyless, NoCaptchaTaskProxyless

class Captcha():

    def __init__(self):
        pass

    def getHCaptcha(self, CLIENT_KEY, WEBSITE_KEY, URL):
        capmonster = HCaptchaTaskProxyless(client_key=CLIENT_KEY)
        taskId = capmonster.createTask(website_key=WEBSITE_KEY, website_url=URL)
        response = capmonster.joinTaskResult(taskId=taskId)
        return response

    def getNoCaptcha(self, CLIENT_KEY, WEBSITE_KEY, URL):
        capmonster = NoCaptchaTaskProxyless(client_key=CLIENT_KEY)
        taskId = capmonster.createTask(website_key=WEBSITE_KEY, website_url=URL)
        response = capmonster.joinTaskResult(taskId=taskId)
        return response

from time import time

if __name__ == "__main__":
    captchasolver = Captcha()
    start_time = time()
    # response = captchasolver.getNoCaptcha('e319ba4186699ecf4b6908f994eb359a', '6LcyQTsUAAAAAI8ba3w-OPXYiz3nUu6H4onGtBPm', 'https://www.canadacomputers.com/login.php')
    response = captchasolver.getHCaptcha('e319ba4186699ecf4b6908f994eb359a', '8c7a977b-4cda-4707-99fd-585679318371', 'https://www.canadacomputers.com')
    print(response)
    print("--- %s seconds ---" % (time() - start_time))