import praw
import json
import requests
import tweepy
import time
import datetime
from pyshorteners import Shortener
import sys
import requests
import json


def main():
    restart = True
    while restart == True:
       # try:
        while True:
            restart = False
            subreddit = setup_connection_reddit(sys.argv[1])
            post_dict, post_ids = tweet_creator(subreddit)
            if post_dict != False:
                tweeter(post_dict, post_ids)
            print "[bot] Sleeping 10 secs"
            time.sleep(10)
       # except Exception, e:
       #     restart = True
       #     print "[bot] Exception caught: ", e
       #     print "[bot] Exception caught - Sleeping 10 secs"
       #     time.sleep(10)

def tweet_creator(subreddit_info):
    post_dict = {}
    post_ids = []
    print "[bot] Getting posts from Reddit"
    for submission in subreddit_info.get_new(limit=1):
        post_dict[strip_title(submission.title)] = submission.url
        post_ids.append(submission.id)

    mini_post_dict = {}
    for post in post_dict:
        post_title = post
        post_link = post_dict[post]
        if notPostedYet(post) :
            short_link = shorten(post_link)
            mini_post_dict[post_title] = short_link
            return mini_post_dict, post_ids
        else:
            print "[bot] Skipped generating short URL"
            return False, False

def getTime():
    return str(datetime.datetime.now())

def setup_connection_reddit(subreddit):
    print "[bot] Start time: " + getTime() + "\n[bot] Setting up connection with reddit/r/"+subreddit
    r = praw.Reddit('Redditwitter' 'monitoring %s' % (subreddit))
    subreddit = r.get_subreddit(subreddit)
    return subreddit

def shortenAdfly(url):
    f = open("adfly.txt")
    lines = f.readlines()
    f.close()
    adflyInfo = lines[1].split(",")
    print "[bot] Shorten the following URL : "+ url 
    shortener = Shortener('AdflyShortener', uid=adflyInfo[1].strip(), key=adflyInfo[0].strip())
    #shortener = Shortener('TinyurlShortener')
    shortUrl = shortener.short(url)
    print "[bot] shortUrl : " + shortUrl
    return shortUrl 

def shorten(url):
    f = open("shorten.txt")
    apiToken = f.readlines()[1].strip()
    f.close()
    response = requests.put("https://api.shorte.st/v1/data/url", {"urlToShorten":url}, headers={"public-api-token": apiToken})
    decoded_response = json.loads(response.content)
    return str(decoded_response['shortenedUrl'])
    

def notPostedYet(id):
    print "[bot] Checking for duplicates"
    notPosted = True
    with open('posted_posts.txt', 'r') as file:
        lines = file.readlines()
        if id in lines[-1]:
            print "[bot] already posted"
            notPosted = False
        else:
            print "[bot] not posted yet..."
    return notPosted

def add_id_to_file(id):
    print "[bot] Adding post to posted_posts.txt : " + str(id)
    with open('posted_posts.txt', 'a') as file:
        file.write(str(id) + "\n")
    file.close()

def strip_title(title):
    if len(title) < 90:
        return title
    else:
        return title[:90] + "..."

def tweeter(post_dict, post_ids):

    twitterAccount = TwitterAccount('twitter.txt')

    for post, post_id in zip(post_dict, post_ids):
        if  notPostedYet(post) :
            twitterAccount.tweet(post.encode('ascii', 'ignore') + " " + post_dict[post])
            add_id_to_file(post.encode('ascii', 'ignore'))

class TwitterAccount:
    def __init__(self, twitterInfoFile):
        f = open(twitterInfoFile)
        lines = f.readlines()
        f.close()
        twitterInfo = lines[1].split(",")
        self.auth = tweepy.OAuthHandler(twitterInfo[2], twitterInfo[3])
        self.auth.set_access_token(twitterInfo[0], twitterInfo[1])
        self.api = tweepy.API(self.auth)
        self.hashtag = twitterInfo[5]
        self.twitterHandle = twitterInfo[4]

    def tweet(self,text):
        print "[bot] " + getTime() + " : Posting the following on twitter"
        print text + " " + self.twitterHandle + " " + self.hashtag 
        self.api.update_status(status=text + " " + self.twitterHandle + " " + self.hashtag)

if __name__ == '__main__':
    main()
