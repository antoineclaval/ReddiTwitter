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
import mimetypes
import ConfigParser
from urlparse import urlparse


def main():
    restart = True
    while restart == True:
        try:
            while True:
                restart = False
                subreddit = setup_connection_reddit(sys.argv[1])
                post_dict, post_ids, author, imageFile = checkReddit(subreddit)
                if post_dict != False:
                    tweeter(post_dict, post_ids, author, imageFile)
                print "[bot] Sleeping " + sys.argv[2] + " minutes"
                time.sleep(num(sys.argv[2]) * 60) 
        except Exception, e:
            restart = True
            print "[bot] Exception caught: ", e
            print "[bot] Exception caught - Sleeping 10 secs"
            time.sleep(10)
#

def checkReddit(subreddit_info):
    post_dict = {}
    post_ids = []
    author = "Unknow"
    print "[bot] Getting posts from Reddit"
    for submission in subreddit_info.get_new(limit=1):
        post_dict[strip_title(submission.title)] = submission.url
        author = submission.author.name.encode('utf-8')
        post_ids.append(submission.id)

    mini_post_dict = {}
    for post in post_dict:
        post_title = post
        post_link = post_dict[post]
        if notPostedYet(post) :
            imageName = False 
            imageName = handleImage(post_link)
            short_link = shorten(post_link)
            mini_post_dict[post_title] = short_link
            return mini_post_dict, post_ids, author, imageName
        else:
            print "[bot] Skipped generating short URL"
            return False, False, False, False

def getTime():
    return str(datetime.datetime.now())

def setup_connection_reddit(subreddit):
    print "[bot] Start time: " + getTime() + "\n[bot] Setting up connection with reddit/r/"+subreddit
    r = praw.Reddit('Redditwitter' 'monitoring %s' % (subreddit))
    subreddit = r.get_subreddit(subreddit)
    return subreddit

def handleImage(url):
    url = handleImgurUrl(url)
    path = urlparse(url).path
    print path 
    maintype= mimetypes.guess_type(path)[0]
    if maintype in ('image/png', 'image/jpeg', 'image/gif'):
        f = open("img"+path,'wb')
        f.write(requests.get(url).content)
        f.close()
        return "img"+path
    return False


def handleImgurUrl(url):
    if ( "imgur" in url): 
        print "imgur detected :"+url
        if( '/a/' in url or 'i.imgur.com' in url or 'imgur.com/gallery' in url):
            # /a/ it's a album. Can't do much. i.imgur = it's already a image nothing to do
            return url 
        else :
            imgurId = url.split("/")
            print  imgurId
            return "http://i.imgur.com/" + imgurId[3] + ".jpeg"

def shorten(url):
    print "shorten : " + url 
    Config = ConfigParser.ConfigParser()
    Config.read("config.ini")
    apiToken = Config.get('shorte.st', 'public-api-token')

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
    if len(title) < 80:
        return title
    else:
        return title[:80] + "..."

def tweeter(post_dict, post_ids, author, imageFile):

    twitterAccount = TwitterAccount()

    for post, post_id in zip(post_dict, post_ids):
        if  notPostedYet(post) :
            twitterAccount.tweet(post.encode('ascii', 'ignore') + " " + post_dict[post] , " @"+author, imageFile)
            add_id_to_file(post.encode('ascii', 'ignore'))

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


class TwitterAccount:
    def __init__(self):
        Config = ConfigParser.ConfigParser()
        Config.read("config.ini")
        self.auth = tweepy.OAuthHandler(Config.get('twitter','consumer_key'), Config.get('twitter', 'consumer_secret'))
        self.auth.set_access_token(Config.get('twitter','access_token'), Config.get('twitter','access_token_secret'))
        self.api = tweepy.API(self.auth)
        self.hashtag = Config.get('twitter', 'hashtag')

    def tweet(self,text,author, media):
        print "[bot] " + getTime() + " : Posting the following on twitter"
        toPost = text + " " + author + " " + self.hashtag 
        if len(toPost) > 140 :
            lentext = 138 - len(author) - len(self.hashtag) # 138 because of spaces
            toPost = toPost[:lentext] + " " + author + " " + self+hashtag 
        print toPost
        if (media == False):
            self.api.update_status(status=toPost)
        else :
            print "upload " + media + " on twitter"
            self.api.update_with_media(media, status=toPost)

if __name__ == '__main__':
    main()
