try:
    import mongo
    from twitter.tweet_setup import Setup
    from twitter.streaming import stream
    from twitter.historic import scrape
    from menu import Menu
except ImportError as e:
    print("Error:", e)
    quit()


class MenuTwitter(Menu):
    def __init__(self,streaming=False):
        super().__init__()
        self.setup = Setup(streaming)

    def menu_stream(self):
        while True:
            inpt = self.get_menu("STREAMING", ["Search = " + (str(self.setup.term).strip('[]') if self.setup.term else self.purple + "None" + self.end),
                                               "Limit = " + str(self.setup.lim),
                                               "Temporary Collection = " + str(self.setup.temp),
                                          "Database Name = '" + self.setup.db_name + "'",
                                          "Collection Name = '" + self.setup.coll_name + "'",
                                          "Languages = " + str(self.setup.lang).strip('[]'),
                                          "Follow UID(s) = " + (str(self.setup.users).strip('[]') if self.setup.users else self.purple + "None" + self.end),
                                          "MongoDB Connected = " + self.purple + str(mongo.connected) + self.end],
                            "*Enter option number or: [Enter] - start streaming, [r] - return.""\n>>>")

            if inpt == '' and mongo.connected and (self.setup.term or self.setup.users):
                self.divider()
                print(self.purple, end='')
                print("Waiting for new tweets...")
                self.setup.init_db()
                print(self.end, end='')
                stream(self.setup)
                print("\n", end='')
                break
            elif inpt == '':
                print(self.purple + "MongoDB must be connected and a search or UID must have been entered." + self.end)
                continue
            elif inpt == 'r':
                return

            menu = {
                1: self.sub_search,
                2: self.sub_lim,
                3: self.sub_tmp,
                4: self.sub_db,
                5: self.sub_coll,
                6: self.sub_lang,
                7: self.sub_follow,
                8: self.mongo_connect
            }
            self.divider()
            menu[inpt]()

    def menu_hist(self):
        while True:
            inpt = self.get_menu("HISTORIC", ["Search = " + (str(self.setup.term).strip('[]') if self.setup.term else self.purple + "None" + self.end),
                                              "Limit = " + ((self.purple + str(self.setup.lim) + self.end) if self.setup.lim is None else str(self.setup.lim)),
                                              "Temporary Collection = " + str(self.setup.temp),
                                              "Database Name = '" + self.setup.db_name + "'",
                                              "Collection Name = '" + self.setup.coll_name + "'",
                                              "Result Type = " + self.setup.result_type,
                                              "Date Range = " + (
                                         (("On/After " + str(self.setup.after) if self.setup.after is not None else "") +
                                          ((", " if self.setup.after is not None and self.setup.before is not None else "") +
                                           ("Before " + str(self.setup.before)) if self.setup.before is not None else ""))
                                         if self.setup.after is not None or self.setup.before is not None else "None"),
                                         "MongoDB Connected = " + self.purple + str(mongo.connected) + self.end],
                            "*Enter option number or: [Enter] - start streaming, [r] - return.""\n>>>")

            if inpt == '' and mongo.connected and self.setup.term and self.setup.lim:
                self.divider()
                print(self.purple, end='')
                self.setup.init_db()
                print("Retrieving tweets...")
                print(self.end, end='')
                scrape(self.setup)
                print("\n", end='')
                break
            elif inpt == '':
                print(
                    self.purple + "MongoDB must be connected, and both a search and limit must have been entered." + self.end)
                continue

            menu = {
                1: self.sub_search,
                2: self.sub_lim,
                3: self.sub_tmp,
                4: self.sub_db,
                5: self.sub_coll,
                6: self.sub_result,
                7: self.sub_date,
                8: self.mongo_connect
            }
            self.divider()
            menu[inpt]()

    def sub_search(self):
        print(self.bold, end='')
        if self.setup.streaming:
            print(self.bold + "*Enter search term(s), separate multiple queries with '||'.")
        else:
            print(self.bold + "*Enter search term(s), use https://dev.twitter.com/rest/public/search for operators.")
        inpt = input("*Leave blank to clear, [" + self.cyan + "r" + self.end + "] - return.\n>>>" + self.end).strip()
        print(self.end, end='')
        self.divider()
        if inpt == 'r':
            print(self.purple + "Search unchanged." + self.end)
            return
        self.setup.set_search(inpt)
        print(self.end, end='')
        print(self.purple + "Search set to " + (
            str(self.setup.term).strip('[]') if self.setup.term else "None") + "." + self.end)

    def sub_lim(self):
        print(self.bold, end='')
        if self.setup.streaming:
            print("*Enter number of tweets to retrieve. Leave blank for unlimited.",end='')
        else:
            print("*Enter number of tweets to retrieve.",end='')
        inpt = self.get_menu('',None, "\n>>>")
        self.divider()
        if inpt == 'r':
            print(self.purple + "Limit unchanged." + self.end)
            return
        if inpt == '':
            self.setup.lim = None
        else:
            self.setup.lim = inpt
        print(self.end, end='')
        print(self.purple + "Limit set to " + str(self.setup.lim) + "." + self.end)


    def sub_tmp(self):
        print(self.purple, end='')
        if not self.setup.temp:
            print("Collection will be marked as Temporary.")
            self.setup.temp = True
        else:
            print("Collection will be marked as Permanent.")
            self.setup.temp = False
        print(self.end, end='')


    def sub_db(self):
        while True:
            inpt = input(self.bold + "Enter a new name for the database, currently '" + self.setup.db_name +
                         "'. Leave blank to cancel.\nSpaces and special characters will be removed.\n>>>" + self.end)
            inpt = ''.join(e for e in inpt if e.isalnum())
            if inpt == '' or inpt == self.setup.db_name or inpt == 'admin' or inpt == 'local':
                break
            self.divider()
            print(self.purple + "Database changed from '" + self.setup.db_name + "' to '" + inpt + "'.")
            self.setup.db_name = inpt
            if mongo.connected:
                if inpt in mongo.get_dbnames():
                    print("'" + inpt + "' already exists. New tweets will be added to existing.")
                else:
                    print("New database '" + inpt + "' will be created.")
            print(self.end, end='')
            break


    def sub_coll(self):
        while True:
            inpt = input(self.bold + "Enter a new name for this collection, currently '" + self.setup.coll_name +
                         "'. Leave blank to cancel.\nPut '[dt]' in name to insert date + time.\n>>>" +
                         self.end).strip().replace("$", "")
            if inpt == '' or inpt == self.setup.coll_name:  # If blank or collection name is same
                break
            if '[dt]' in inpt:  # inserting and replacing [dt] with date/time
                self.setup.coll_name = inpt.replace('[dt]', str(self.setup.get_dt())).strip()
            else:
                self.setup.coll_name = inpt
            self.divider()
            print(self.purple + "Collection changed to '" + self.setup.coll_name + "'.")
            if mongo.connected:
                if self.setup.coll_name in mongo.get_collections(self.setup.db_name):
                    print("'" + self.setup.coll_name + "' already exists. New tweets will be added to existing.")
                else:
                    print("New collection will be created.")
            print(self.end, end='')
            break


    def sub_lang(self):
        langs = ['en', 'ar', 'bn', 'cs', 'da', 'de', 'el', 'es', 'fa', 'fi', 'fil', 'fr', 'he', 'hi', 'hu', 'id',
                 'it',
                 'ja', 'ko', 'msa', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sv', 'th', 'tr', 'uk', 'ur', 'vl', 'zh-cn',
                 'zh-tw']
        inpt = input(self.bold + "Enter a comma separated list of language codes. "
                                  "https://dev.twitter.com/web/overview/languages\n>>>").replace(" ", '').split(',')
        if inpt == '':
            return
        self.divider()
        tmp = []
        for i in inpt:
            if i in langs and i not in tmp:
                tmp.append(i)
        if len(tmp) >= 1:
            print(self.purple + "Accepted languages: " + str(tmp).strip("[]") + "." + self.end)
            self.setup.lang = tmp


    def sub_follow(self):
        print(self.bold, end='')
        print("Use http://gettwitterid.com to get a UID from a username. Must be a numeric value.")
        inpt = input(self.bold + "*Enter UID(s), separate with '||'. Leave blank for no user tracking, [" + self.cyan +
                     "r" + self.end + "] - return/cancel.\n>>>" + self.end).strip()
        if inpt == 'r':
            return
        self.divider()
        self.setup.set_follow(inpt)
        print(self.end, end='')
        print(self.purple + "Follow list changed to " + (
            str(self.setup.users).strip('[]') if self.setup.users else "None") + "." + self.end)

    def sub_result(self):
        inpt = input(self.bold + "*Enter a result type: 'mixed','recent', or 'popular'.\n>>>" + self.end).strip()
        self.setup.set_result_type(inpt)
        print(self.purple + "Result type set to " + self.setup.result_type + "." + self.end)

    def sub_date(self):
        inpt = input(
            self.bold + "*Enter cut off date(s). Must be: B/A-YYYY-MM-DD and no older than 7 days.\n"
                         "*B=Before (<), A=After (>=). Use '||' to separate.\n*Ex: 'b-2017-5-22||a-2017-5-20'. "
                         "Leave blank to clear, [" + self.cyan + "r" + self.end + "] - cancel.\n>>>" + self.end)
        inpt = inpt.strip().replace(" ", "")
        if inpt == "":
            self.setup.until = None
            self.setup.after = None
            return
        elif inpt == "r":
            return
        self.divider()
        print(self.purple, end="")
        self.setup.set_date(inpt)
        print(self.end, end="")


