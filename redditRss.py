import praw
import datetime
import time
from feedgen.feed import FeedGenerator

def readSecrets():
    with open("redditAppData", "r") as f:
        lines = [l.rstrip("\n") for l in f.readlines()]
        client_id, client_secret, user_agent = lines
    return {
            "client_id":client_id, 
            "client_secret":client_secret, 
            "user_agent" : user_agent
            }

reddit = praw.Reddit(**readSecrets())

def readTopPosts(subredditName):
    submissions = reddit.subreddit(subredditName).top(limit=10, time_filter="day")
    return submissions

def generateRss(submissions, outputFile, title, description, link):
    feedGen = FeedGenerator()
    feedGen.id('http://reddit.com/r/dota2/top')
    feedGen.title(title)
    feedGen.link({"href":link})
    feedGen.description(description)
    for submission in submissions:
        feedItem = feedGen.add_entry()
        submissionItem(feedItem, submission)
    feedGen.rss_str(pretty=True)
    feedGen.rss_file(outputFile)
    
def submissionItem(feedEntry, submission):
    feedEntry.title(submission.title)
    feedEntry.id(submission.url)

def generateSubredditRss(subredditName):
    generateRss(
            readTopPosts(subredditName), 
            "{}.xml".format(subredditName), 
            "Top posts {}".format(subredditName),
            "Top posts {}".format(subredditName),
            "reddit.com/r/{}/top".format(subredditName)
            )

while True:
    generateSubredditRss("dota2")
    time.sleep(600)
