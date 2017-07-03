try:
    import mongo
except ImportError as e:
    print("Import Error in menu.py:",e)


class Menu:
    def __init__(self):
        # Text colors
        self.purple = "\033[1;94m"
        self.cyan = '\033[36m'
        self.bold = '\033[1m'
        self.end = '\033[1;0m'
    
    def header(self,text): # ---header text---
        print(self.cyan + self.bold + ('-' * int((40 - len(text)) / 2)) + self.bold +
              text + self.cyan + self.bold + ('-' * int((40 - len(text)) / 2)) + self.end)
    
    def divider(self): # ----------
        print(self.cyan + self.bold + '-' * 40 + self.end)
    
    def get_menu(self,head, menu, input_menu):
        # Numbered user input menu
        while True:
            if menu is not None:
                self.header(head)
                for num, entry in enumerate(menu): # Print entries
                    print("[" + self.purple + str(num + 1) + self.end + "] - " + entry)
                self.divider()
            #Stylize input menu
            entry = input(self.bold + input_menu.replace("[", self.end +
                                "[" + self.purple).replace("]",self.end + "]") + self.end).replace(" ", "")
            if entry == 'q': # input 'q' to quit
                quit()
            elif entry == 'r' or entry == '': # Returns r or space for menus to handle it.
                return entry
            try: # Type cast num input to int
                entry = int(entry)
            except ValueError:
                continue
            if ((entry > len(menu)) if menu is not None else False) or entry < 1:
                # (Compare entry to menu size if the menu exists, otherwise False) OR if input is < 1
                continue # Recognize as invalid input
            return entry # Successfully return input for menus to handle
    
    def get_db(self):
        # Create menu to list Databases
        if not mongo.connected:
            print(self.purple + "You must be connected to MongoDB!" + self.end)
            return
    
        print(self.purple + "Do not select 'admin' or 'local' databases." + self.end)
        db_list = []
        for j, k in enumerate(mongo.get_dbnames(), 1):  # start at 1
            db_list.append( k + "' (" + str(len(mongo.get_collections(k))) + ")")  # print databases
        inpt = self.get_menu("DATABASES",db_list, "*Select a db to view collections or [r] - return.\n>>>")
        if inpt == 'r' or inpt == '':
            return
    
        db = mongo.client[mongo.get_dbnames()[inpt - 1]]  # set up chosen db
        coll = mongo.get_collections(mongo.get_dbnames()[inpt - 1])  # collections list from that db
        return coll, db
    
    
    def get_coll(self):
        # Create menu to list collections
        try:
            coll, db = self.get_db()
        except BaseException:
            return None
        coll_list = []
        for j, k in enumerate(coll, 1):
            tmp = db[coll[j - 1]].find({"t_temp": True})
            doc_count = db[coll[j - 1]].find({})  # take the specified collection, and find all the documents
            coll_list.append(k + "' (" + str(doc_count.count()) + ")" + ("(TEMP)" if tmp.count() > 0 else ""))
            tmp.close()
            doc_count.close()
        inpt = self.get_menu("COLLECTIONS",coll_list, "*Select a collection or [r] - return.\n>>>")
    
        if inpt == 'r' or inpt == '':
            return
        return db[coll[inpt - 1]]

    def mongo_connect(self):
        # Connect to MongoDB
        self.divider()
        print(self.purple, end='')
        mongo.mongo_connection()
        print(self.end, end='')
