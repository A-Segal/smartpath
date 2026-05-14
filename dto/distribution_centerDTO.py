class DistributionCenterDTO:
    def __init__(self,id,fname,lname,password,
     username,

        mail,
        phone,
        location_lat,
        location_lng,
        request
    ):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.username = username
        self.password = password
        self.mail = mail
        self.phone = phone
        self.location_lat = location_lat
        self.location_lng = location_lng
        self.request = request