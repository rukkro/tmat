try:
    import config,mongo,requests
    from display import color,get_menu
    import tweepy, json, string, datetime
    from tweepy import Stream
    from tweepy import OAuthHandler
    from tweepy.streaming import StreamListener
    from http.client import IncompleteRead
    from difflib import SequenceMatcher
except ImportError as e:
    print("Error:", e)
    quit()

auth = OAuthHandler(config.ckey, config.csecret)
auth.set_access_token(config.atoken, config.asecret)
api = tweepy.API(auth)

class Listener(StreamListener):
    def __init__(self, lim, coll, sim):
        self.count = 0
        self.lim = lim
        self.coll = coll
        self.sim = sim

    def on_data(self, data):
        if self.count == self.lim:
            raise KeyboardInterrupt #easy way to return to menus

        json_data = json.loads(data)
        if self.json_filter(json_data):
            if not self.duplicate_find(json_data):  # if no duplicates found, add tweet to db
                self.count += 1
                self.coll.insert_one(json_data)
            if self.lim is not None:
                print("\rTweets:", self.count,
                      "[{0:50s}] {1:.1f}% ".format('#' * int((self.count / int(self.lim)) * 50),
                                                   (self.count / int(self.lim)) * 100), end="", flush=True)
            else:
                print("\rTweets:", self.count, end="", flush=True)
            return True

    def duplicate_find(self, json_data):
        cursor = self.coll.find({'user.screen_name': json_data['user']['screen_name']})
        for c in cursor:  # searching for exact same tweets from same user, removing spaces and punct.
            coll_tweet = c['text'].translate(c['text'].maketrans('', '', string.punctuation)).replace(" ", "")
            json_tweet = json_data['text'].translate(json_data['text'].maketrans('', '', string.punctuation)).replace(" ", "")

            if coll_tweet == json_tweet:
                if config.verbose:
                    print(" FIRST: " + c['text'] + " SECOND: " + json_data['text'])
                    print("\nDuplicate tweet from " + "@" + json_data['user']['screen_name'] + " ignored.")
                cursor.close()
                return True
            elif SequenceMatcher(None,coll_tweet,json_tweet).ratio() > self.sim:
                if config.verbose:
                    print("\n" + str(SequenceMatcher(None,coll_tweet,json_tweet).ratio() * 100) + "% similar existing"
                        " tweet from " + "@" + json_data['user']['screen_name'] + " ignored.")
                    print(" FIRST: " + c['text'] + " SECOND: " + json_data['text'])
                cursor.close()
                return True

        cursor.close()
        return False  # if no duplicates found

    def json_filter(self, json_data):  #removes certain tweets
        if "created_at" not in json_data or "retweeted_status" in json_data or \
                        "quoted_status" in json_data or json_data["in_reply_to_user_id"] != None:
            return False
        else:
            return True  # does NOT affect tweet streaming. Whether or not tweet saved

    def on_error(self, status):
        print("Error code:", status, end=". ")
        if status == 406:
            print("Invalid tweet search request.")
        if status == 401:
            print("Authentication failed. Check your keys and verify your system clock is accurate.")
        if status == 420:
            print("Rate limit reached. Wait a bit before streaming again.")
        print(color.YELLOW + "Streaming stopped." + color.END)
        quit()


class Setup: #settings and setup for tweet scraping
    def __init__(self):
        self.temp = False
        self.img = False
        self.lim = None
        self.db_name = 'twitter'
        self.dt = str(datetime.datetime.now())
        self.sim = .55
        self.lang = ['en']
        self.coll_name = self.dt
        self.term = []
        self.users = []

    def limit(self):
        inpt = get_menu(None,"*Enter number of tweets to retrieve. Leave blank for unlimited.\n>>>")
        if inpt == 'r':
            return
        if inpt == '':
            self.lim = None
        else:
            self.lim = inpt

    def search(self):
        tmp = [] #stores user input to filter out invalid responses
        i = input(color.BOLD + "*Enter search term(s), separate multiple queries with '||'.\n>>>" + color.END).strip()
        if i == 'r':
            return
        self.term[:] = []
        if i == '':
            self.coll_name = self.dt
            return
        tmp = i.split('||') #split into list by ||
        for i in range(len(tmp)):
            tmp[i] = tmp[i].strip()  #remove outside spacing from all entries
            if tmp[i] == '': #if blank after spaces removed, dont append to search term list
                continue
            self.term.append(tmp[i])
        if len(self.term) == 0: #if nothing appended to search term list, return.
            return
        self.coll_name = self.term[0] + " - " + self.dt #set initial collection name

    def follow(self):# https://twitter.com/intent/user?user_id=XXX
        tmp = []
        print("Use http://gettwitterid.com to get a UID from a username. Must be a numeric value.")
        i = input(color.BOLD + "*Enter UID(s), separate with '||'. Leave blank for no user tracking, [r] - "
                               "return/cancel.\n>>>" + color.END).strip()
        if i == 'r':
            return
        self.users[:] = []  # clear list
        if i == '': #if blank, then clear list beforehand
            return
        tmp = i.split('||')
        for i in range(len(tmp)):
            tmp[i] = tmp[i].replace(" ","")
            if tmp[i] == '' or not tmp[i].isdigit():  # if blank/not a num, dont append to search term list
                continue
            print("Verifying potential UID...")   #this could break if twitter changes their website
            try:
                if requests.get("https://twitter.com/intent/user?user_id=" + tmp[i]).status_code != 200:
                    if input("UID '" + tmp[i] + "' not found, attempt to follow anyway? [y/n]:").replace(" ","") == 'y':
                        self.users.append(tmp[i])
                else:
                    print("UID '" + tmp[i] + "' found!")
                    self.users.append(tmp[i])
            except requests.exceptions.ConnectionError:
                print("Connection failed. UID's will not be verified.")
                self.users.append(tmp[i])

def stream(search, lim, coll_name, db_name, temp, simil, lang, users):
    try:
        print(color.YELLOW + "Initializing DB and Collection...")
        db = mongo.client[db_name]  # initialize db
        tweetcoll = db[coll_name]  # initialize collection
        c_true = tweetcoll.find({"t_temp":True})
        c_false = tweetcoll.find({"t_temp":False})
        doc_count = c_true.count() + c_false.count()

        if doc_count > 0: #if there's already t_temp doc
            tweetcoll.update_many({"t_temp":not temp},{'$set':{"t_temp":temp}})
        else:
            tweetcoll.insert_one({ #This creates a coll even if no tweets found.
                "t_temp" : temp
            })
        c_true.close()
        c_false.close()
    except BaseException as e:
        print("Error:",e)
        return

    listener = None
    while True: #start streaming
        try:
            listener = Listener(lim, tweetcoll, simil)
            print("Waiting for new tweets..." + color.END)
            twitter_stream = Stream(auth, listener)
            twitter_stream.filter(track=search, languages=lang, follow=users) #location search is not a filter
        except KeyboardInterrupt:
            print("\n")
            return
        except IncompleteRead:
            print("Incomplete Read - Skipping to newer tweets.\n")
        except requests.exceptions.ConnectionError:
            print("Connection Failed - Check your internet.")
            return
        except Exception as e:
            lim-=listener.count #subtracts downloaded tweets from the limit for next round
            print("Error: ",e,"\nAttempting to continue...\n")
            continue

if __name__ == '__main__':
    try:
        s = Setup()
        mongo.mongo_connection()
        s.search()
        if mongo.connected:
            stream(s.term, s.limit(), s.coll_name, s.db_name, s.temp, s.sim, s.lang,s.users)
        else:
            print("MongoDB not connected.")
    except BaseException as e:
        print("Error:",e)