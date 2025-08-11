import badge

class App(badge.BaseApp):
    def on_open(self):
        self.logger.info("this app just launched!")
        badge.utils.set_led(True)
    
    def loop(self):
        pass