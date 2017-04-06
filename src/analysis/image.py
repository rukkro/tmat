import requests, base64,config, os

auth_headers={
    'app_id': config.appid,
    'app_key': config.appkey
}
def get_image(response):
    with open('ta-image.jpg','wb') as f: #convert response into saved image
        f.write(response.content)
    return "ta-image.jpg"

def image_base64(file): #makes image usable for detect()
    with open(file,'rb') as img:
        return base64.b64encode(img.read()).decode('ascii')

def emotion(img):
    url = 'https://api.kairos.com/v2/media'
    with open(img,'rb') as img:
        response = requests.post(url, files={'source': img}, data={'timeout':60}, headers=auth_headers)
    if config.verbose:
        print(response.json())
    return response.json()

def detect(img):
    url = 'https://api.kairos.com/detect'
    response = requests.post(url,json={'image':image_base64(img)},headers=auth_headers)
    if config.verbose:
        print(response.json())
    return response.json()

#https://dev.twitter.com/basics/user-profile-images-and-banners
def insert_data(coll):
    success = 0
    print("Running Image analysis...")
    cursor = coll.find({})  # finds all documents in collection
    for i in cursor:  # loop through those
        profile_pic =i['user']['profile_image_url_https'].replace("_normal","")
        response = requests.get(profile_pic)
        if response.status_code == 404 or response.status_code == 403: #dead links to images
            continue
        if not i['user']['default_profile_image'] and 'default_profile' not in profile_pic: #filter both default pics
            if config.verbose:
                print(profile_pic + " " + i['user']['screen_name'])
            img = get_image(response)
            det = detect(img)
            if 'Errors' in det:
                print("Error:", det['Errors'][0]['ErrCode'] , "-", det['Errors'][0]['Message'] + ". Moving onto the next...")
                continue

            emo =emotion(img)
            coll.update_one({'_id': i.get('_id')}, {'$set': {
                "face": {
                    "emotion":emo,
                    "detection": det
                }}})
            success+=1
        else:
            if config.verbose:
                print(profile_pic+ " DEFAULT PICTURE, IGNORED." + " " + i['user']['screen_name'])
            continue
    os.remove("ta-image.jpg")
    print("Finished: " + str(success) + " of " + str(cursor.count()) + " successfully processed and inserted!")
