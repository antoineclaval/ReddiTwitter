import praw
import json
import requests
import tweepy
import time
import datetime


def main():
    restart = True
    while restart == True:
        try:
            while True:
                restart = False
                subreddit = setup_connection_reddit('sydney')
                post_dict, post_ids = tweet_creator(subreddit)
                if post_dict != False:
                    tweeter(post_dict, post_ids)
                print "[bot] Sleeping 10 secs"
                time.sleep(10)
        except Exception, e:
            restart = True
            print "[bot] Exception caught: ", e
            print "[bot] Exception caught - Sleeping 10 secs"
            time.sleep(10)

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
        if duplicate_check(post) == False:
            print "[bot] Generating short url using goo.gl"
            short_link = shorten(post_link)
            mini_post_dict[post_title] = short_link
            return mini_post_dict, post_ids
        else:
            print "[bot] Skipped generating short URL"
            return False, False

def setup_connection_reddit(subreddit):
    time = datetime.datetime.now().time()
    print "[bot] Start time: " + str(time) + "\n[bot] Setting up connection with Reddit"
    r = praw.Reddit('SydneyReddit' 'monitoring %s' % (subreddit))
    subreddit = r.get_subreddit(subreddit)
    return subreddit

def shorten(url):
    print "[bot] Starting URL shortening process"
    f = open('SydneyReddit.txt')
    lines = f.readlines()
    f.close()
    key = lines[4].strip()
    # print "[bot] Key is: " + key
    headers = {'content-type': 'application/json'}
    payload = {"longUrl": url}
    url = "https://www.googleapis.com/urlshortener/v1/url?key=" + key
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    link = json.loads(r.text)['id']
    return link

def duplicate_check(id):
    print "[bot] Checking for duplicates"
    found = False
    with open('posted_posts.txt', 'r') as file:
        lines = file.readlines()
        if id in lines[-1]:
            print "[bot] Duplicate found"
            found = True
        else:
            print "[bot] Duplicate not found"
    return found

def add_id_to_file(id):
    print "[bot] Adding post to posted_posts.txt : " + str(id)
    with open('posted_posts.txt', 'a') as file:
        file.write(str(id) + "\n")
        file.close()

def strip_title(title):
    if len(title) < 115:
        return title
    else:
        return title[:114] + "..."

def tweeter(post_dict, post_ids):
    f = open('SydneyReddit.txt')
    lines = f.readlines()
    f.close()
    access_token = lines[0].strip()
    access_token_secret = lines[1].strip()
    consumer_key = lines[2].strip()
    consumer_secret = lines[3].strip()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    for post, post_id in zip(post_dict, post_ids):
        # found = duplicate_check(post)
        # if found == 0:
        print "[bot] Posting the following on twitter"
        print post.encode('ascii', 'ignore') + " " + post_dict[post] + " #Sydney"
        api.update_status(status=post.encode('ascii', 'ignore') + " " + post_dict[post] + " #Sydney")
        add_id_to_file(post.encode('ascii', 'ignore'))
        print "[bot] Sleeping for 10 secs"
        time.sleep(10)
        # else:
        #     print "[bot] Already posted"
        #     print "[bot] Sleeping for 10 secs"
        #     time.sleep(10)

if __name__ == '__main__':
    main()
