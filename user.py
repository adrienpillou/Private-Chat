class User():
    def __init__(self, username, password) -> None:
        self.username= username
        self.password= password
        self.color= "white"
    
    def set_color(self, color):
        self.color = color

