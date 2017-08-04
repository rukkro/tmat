try:
    from menu import Menu
    from analysis import menu_analysis
    from twitter import menu_twitter
    import menu_manage, export, config
except ImportError as e:
    print("Import Error in menu_main.py:",e)

class MenuMain(Menu):
    def __init__(self):
        super().__init__()

    def main(self):
        menu = {
            1: menu_twitter.MenuTwitter(True).menu_stream,  # Pass if it's streaming or not
            2: menu_twitter.MenuTwitter(False).menu_hist,
            3: menu_analysis.MenuText().menu_analysis,
            4: export.MenuExport().menu_export,
            5: menu_manage.MenuManage().menu_manage,
            6: self.mongo_connection
        }
        if config.startup_connect:
            self.mongo_connection()
        while True:
            i = self.get_menu("MAIN", ["Stream Tweets.",
               "Historic Tweets.",
               "Analyze Tweets.",
               "Export as CSV.",
               "Manage Collections.",
               "MongoDB Connected = " + self.colors['purple'] + str(self.is_connected()) + self.colors['end']],
                "*Enter option number or [q] - quit.\n>>>")
            try:
                menu[i]()
            except KeyError:
                pass


if __name__ == "__main__":
    try:
        MenuMain().main()
    except KeyboardInterrupt:
        pass
