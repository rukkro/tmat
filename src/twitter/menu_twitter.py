try:
    import mongo
    from twitter.tweet_setup import Setup
    from twitter.streaming import stream
    from twitter.historic import scrape
    from menu import get_menu, Color,divider
except ImportError as e:
    print("Error:", e)
    quit()

def sub_search(s):
    print(Color.BOLD, end='')
    if s.streaming:
        print(Color.BOLD + "*Enter search term(s), separate multiple queries with '||'.")
    else:
        print(Color.BOLD + "*Enter search term(s), use https://dev.twitter.com/rest/public/search for operators.")
    inpt = input("*Leave blank to clear, [r] - return.\n>>>" + Color.END).strip()
    print(Color.END,end='')
    divider()
    if inpt == 'r':
        return
    s.set_search(inpt)
    print(Color.END, end='')
    print(Color.PURPLE + "Search set to " + (
        str(s.term).strip('[]') if s.term else "None") + "." + Color.END)

def sub_lim(s):
    print(Color.BOLD, end='')
    if s.streaming:
        print("*Enter number of tweets to retrieve. Leave blank for unlimited.",end='')
    else:
        print("*Enter number of tweets to retrieve.",end='')
    inpt = get_menu('',None, "\n>>>")
    divider()
    if inpt == 'r':
        return
    if inpt == '':
        s.lim = None
    else:
        s.lim = inpt
    print(Color.END, end='')
    print(Color.PURPLE + "Limit set to " + str(s.lim) + "." + Color.END)


def sub_tmp(s):
    print(Color.PURPLE, end='')
    if not s.temp:
        print("Collection will be marked as Temporary.")
        s.temp = True
    else:
        print("Collection will be marked as Permanent.")
        s.temp = False
    print(Color.END, end='')


def sub_db(s):
    while True:
        inpt = input(Color.BOLD + "Enter a new name for the database, currently '" + s.db_name +
                     "'. Leave blank to cancel.\nSpaces and special characters will be removed.\n>>>" + Color.END)
        inpt = ''.join(e for e in inpt if e.isalnum())
        if inpt == '' or inpt == s.db_name or inpt == 'admin' or inpt == 'local':
            break
        divider()
        print(Color.PURPLE + "Database changed from '" + s.db_name + "' to '" + inpt + "'.")
        s.db_name = inpt
        if mongo.connected:
            if inpt in mongo.get_dbnames():
                print("'" + inpt + "' already exists. New tweets will be added to existing.")
            else:
                print("New database '" + inpt + "' will be created.")
        print(Color.END, end='')
        break


def sub_coll(s):
    while True:
        inpt = input(Color.BOLD + "Enter a new name for this collection, currently '" + s.coll_name +
                     "'. Leave blank to cancel.\nPut '[dt]' in name to insert date + time.\n>>>" +
                     Color.END).strip().replace("$", "")
        if inpt == '' or inpt == s.coll_name:  # If blank or collection name is same
            break
        if '[dt]' in inpt:  # inserting and replacing [dt] with date/time
            s.coll_name = inpt.replace('[dt]', str(s.get_dt())).strip()
        else:
            s.coll_name = inpt
        divider()
        print(Color.PURPLE + "Collection changed to '" + s.coll_name + "'.")
        if mongo.connected:
            if s.coll_name in mongo.get_collections(s.db_name):
                print("'" + s.coll_name + "' already exists. New tweets will be added to existing.")
            else:
                print("New collection will be created.")
        print(Color.END, end='')
        break


def sub_lang(s):
    langs = ['en', 'ar', 'bn', 'cs', 'da', 'de', 'el', 'es', 'fa', 'fi', 'fil', 'fr', 'he', 'hi', 'hu', 'id',
             'it',
             'ja', 'ko', 'msa', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sv', 'th', 'tr', 'uk', 'ur', 'vl', 'zh-cn',
             'zh-tw']
    inpt = input(Color.BOLD + "Enter a comma separated list of language codes. "
                              "https://dev.twitter.com/web/overview/languages\n>>>").replace(" ", '').split(',')
    if inpt == '':
        return
    divider()
    tmp = []
    for i in inpt:
        if i in langs and i not in tmp:
            tmp.append(i)
    if len(tmp) >= 1:
        print(Color.PURPLE + "Accepted languages: " + str(tmp).strip("[]") + "." + Color.END)
        s.lang = tmp


def sub_follow(s):
    print(Color.BOLD, end='')
    print("Use http://gettwitterid.com to get a UID from a username. Must be a numeric value.")
    inpt = input(Color.BOLD + "*Enter UID(s), separate with '||'. Leave blank for no user tracking, [r] - "
                           "return/cancel.\n>>>" + Color.END).strip()
    if inpt == 'r':
        return
    divider()
    s.set_follow(inpt)
    print(Color.END, end='')
    print(Color.PURPLE + "Follow list changed to " + (
        str(s.users).strip('[]') if s.users else "None") + "." + Color.END)


def sub_mongo(s):
    print(Color.PURPLE, end='')
    mongo.mongo_connection()
    print(Color.END, end='')

def menu_stream():
    divider()
    s = Setup(True)
    sub_search(s)
    while True:
        inpt = get_menu("STREAMING", ["Search = " + (str(s.term).strip('[]') if s.term else "None"),
                         "Limit = " + str(s.lim),
                         "Temporary Collection = " + str(s.temp),
                         "Database Name = '" + s.db_name + "'",
                         "Collection Name = '" + s.coll_name + "'",
                         "Languages = " + str(s.lang).strip('[]'),
                         "Follow UID(s) = " + (str(s.users).strip('[]') if s.users else "None"),
                         "MongoDB Connected = " + Color.PURPLE + str(mongo.connected) + Color.END],
                        "*Enter option number or: [Enter] - start streaming, [r] - return.""\n>>>")

        if inpt == '' and mongo.connected and (s.term or s.users):
            divider()
            print(Color.PURPLE, end='')
            print("Waiting for new tweets...")
            s.init_db()
            print(Color.END,end='')
            stream(s)
            print("\n",end='')
            break
        elif inpt == '':
            print(Color.PURPLE + "MongoDB must be connected and a search or UID must have been entered." + Color.END)
            continue
        elif inpt == 'r':
            return

        menu = {
            1: sub_search,
            2: sub_lim,
            3: sub_tmp,
            4: sub_db,
            5: sub_coll,
            6: sub_lang,
            7: sub_follow,
            8: sub_mongo
        }
        divider()
        menu[inpt](s)
def sub_result(s):
    inpt = input(Color.BOLD + "*Enter a result type: 'mixed','recent', or 'popular'.\n>>>" + Color.END).strip()
    s.set_result_type(inpt)
    print(Color.PURPLE + "Result type set to " + s.result_type + "." + Color.END)

def sub_date(s):
    inpt = input(
        Color.BOLD + "*Enter cut off date(s). Must be: B/A-YYYY-MM-DD and no older than 7 days.\n"
                     "*B=Before (<), A=After (>=). Use '||' to separate.\n*Ex: 'b-2017-5-22||a-2017-5-20'. "
                     "Leave blank to clear, [r] - cancel.\n>>>" + Color.END)
    inpt = inpt.strip().replace(" ", "")
    if inpt == "":
        s.until = None
        s.after = None
        return
    elif inpt == "r":
        return
    divider()
    print(Color.PURPLE, end="")
    s.set_date(inpt)
    print(Color.END,end="")

def menu_hist():
    divider()
    s = Setup()
    sub_search(s)
    divider()
    sub_lim(s)
    while True:
        inpt = get_menu("HISTORIC", ["Search = " + (str(s.term).strip('[]') if s.term else "None"),
                         "Limit = " + str(s.lim),
                         "Temporary Collection = " + str(s.temp),
                         "Database Name = '" + s.db_name + "'",
                         "Collection Name = '" + s.coll_name + "'",
                                     "Result Type = " + s.result_type,
                         "Date Range = " + ((("On/After " + str(s.after) if s.after is not None else "") +
                                             ((", " if s.after is not None and s.before is not None else "") +
                                              ("Before " + str(s.before)) if s.before is not None else ""))
                                            if s.after is not None or s.before is not None else "None"),
                         "MongoDB Connected = " + Color.PURPLE + str(mongo.connected) + Color.END],
                        "*Enter option number or: [Enter] - start streaming, [r] - return.""\n>>>")

        if inpt == '' and mongo.connected and s.term and s.lim:
            divider()
            print(Color.PURPLE, end='')
            s.init_db()
            print("Retrieving tweets...")
            print(Color.END,end='')
            scrape(s)
            print("\n",end='')
            break
        elif inpt == '':
            print(Color.PURPLE + "MongoDB must be connected, and both a search and limit must have been entered." + Color.END)
            continue

        menu = {
            1: sub_search,
            2: sub_lim,
            3: sub_tmp,
            4: sub_db,
            5: sub_coll,
            6: sub_result,
            7: sub_date,
            8: sub_mongo
        }
        divider()
        menu[inpt](s)
