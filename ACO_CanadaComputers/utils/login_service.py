import requests

class CustomerLogin():
    
    def __init__(self, username, password):
        self.s = requests.Session()
        self.username = username
        self.password = password

    def getSID(self):
        #------------------------Go to the login page to get the session ID----------
        headersCheck = {
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
            'Referer': 'https://www.canadacomputers.com',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = self.s.get('https://www.canadacomputers.com/login.php' , headers=headersCheck)

        if response.status_code != 200:
            print(f'Error getting page{response.status_code}')

        params = (('sid', self.s.cookies['sid']),)
        #--------------------------------------------------------------------------

        #------------------------Log In-------------------------------------------
        data = {
            'lo-type': 'regular_customer',
            'lo-username': self.username,
            'lo-password': self.password,
            'login': '',
            'g-recaptcha-response': ''
        }

        headersPost = {
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
            'Referer': 'https://www.canadacomputers.com/login.php',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = self.s.post('https://www.canadacomputers.com/login.php', headers=headersPost, params=params, data=data)

        file = open('ACO_CanadaComputers/utils/proofs/login-confirmation.html', 'w')
        file.write(response.text)

        if "Logout" in response.text:
            SID = self.s.cookies['sid']
            print(f'{self.username} logged in with SID {SID}!')
            return SID
        elif "No match for User Name or Password." in response.text:
            print('Failed due to wrong email or password')

        

if __name__ == "__main__":
    loginItem = CustomerLogin('Justicechu09@gmail.com', 'pcar1234')
    print(loginItem.getSID())