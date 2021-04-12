class Customer():

    def __init__(self, firstname, lastname, areacode, three, four, email, password, carddigits, cardname, locations, sid, gpus):
        self.firstname = firstname
        self.lastname = lastname
        self.areacode = areacode
        self.three = three
        self.four = four
        self.email = email
        self.password = password
        self.carddigits = carddigits
        self.cardname = cardname
        self.locations = locations
        self.gpus = gpus
        self.sid = sid

    def __str__(self):
        return f'This customer is {self.firstname} {self.lastname} and has a session ID of {self.sid}. The email is {self.email} and the password is {self.password}' 
    
    def setSID(self, sid):
        self.sid = sid