import praw
import PyRSS2Gen as rssGen
import datetime

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
    submissions = reddit.subreddit("learnpython").top(limit=10, time_filter="day")
    return submissions

def generateRss(outputFile, title, submissions):
    rss =rssGen.RSS2(
        title="cool feed title",
        link="??",
        description="cool feed",
        lastBuildDate=datetime.datetime.now(),
        items=[submissionItem(submission) for submission in submissions]
    )
    rss.write_xml(open(outputFile, "w"))
    
def submissionItem(submission):
    return rssGen.RSSItem(
        title=submission.title,
        link=submission.url,
        description="hello",
        guid = rssGen.Guid(submission.url),
        pubDate=datetime.datetime.now()
    )

def generateSubredditRss(subredditName):
    generateRss("out.xml", subredditName, readTopPosts(subredditName))

generateSubredditRss("learnpython")
