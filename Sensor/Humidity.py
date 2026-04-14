class Humidity:
    def __init__(self, value, time):
        self.__value = value
        self.__timestamp = time

    def get_value(self):
        return self.__value
    
    def get_timestamp(self):
        return self.__timestamp
