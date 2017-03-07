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

def readTopPosts(subredditName, numPosts):
    submissions = reddit.subreddit(subredditName).top(limit=numPosts, time_filter="day")
    return submissions

def generateRss(submissions, outputFile, title, description, link, _id):
    feedGen = FeedGenerator()
    feedGen.id(_id)
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
    feedEntry.id(submission.url + "/")
    feedEntry.link({"href":submission.shortlink})
    feedEntry.description(submission.selftext)

def generateSubredditRss(subredditName, numPosts):
    generateRss(
            submissions=readTopPosts(subredditName, numPosts),
            outputFile="feeds/{}.xml".format(subredditName),
            title="Top posts {}".format(subredditName),
            description="Top posts {}".format(subredditName),
            link="reddit.com/r/{}/top".format(subredditName),
            _id="reddit.com/r/{}/top".format(subredditName)
            )

def getSubredditList():
    with open("subreddits", "r") as f:
        for l in f.readlines():
            name, numPosts = l.replace("\n", "").split()
            numPosts = int(numPosts)
            yield name, numPosts

for (subreddit, numPosts) in getSubredditList():
    generateSubredditRss(subreddit, numPosts)
