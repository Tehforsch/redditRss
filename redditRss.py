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

def readTopPosts(subredditName, numPosts, filters):
    if filters != []:
        submissions = list(reddit.subreddit(subredditName).top(limit=numPosts*3, time_filter="day"))
        submissions = [submission for (i, submission) in enumerate(submissions) if (i < numPosts) and not any(flairToFilter.lower() in submission.link_flair_text.lower() for flairToFilter in filters)]
    else:
        submissions = reddit.subreddit(subredditName).top(limit=numPosts, time_filter="day")
    return list(submissions)

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

def generateSubredditRss(subredditName, numPosts, filters):
    generateRss(
            submissions=readTopPosts(subredditName, numPosts, filters),
            outputFile="feeds/{}.xml".format(subredditName),
            title="Top posts {}".format(subredditName),
            description="Top posts {}".format(subredditName),
            link="reddit.com/r/{}/top".format(subredditName),
            _id="reddit.com/r/{}/top".format(subredditName)
            )

def getSubredditList():
    with open("subreddits", "r") as f:
        for l in f.readlines():
            name, numPosts, *filters = l.replace("\n", "").split()
            numPosts = int(numPosts)
            yield (name, numPosts, filters)

for (subreddit, numPosts, *filters) in getSubredditList():
    generateSubredditRss(subreddit, numPosts, *filters)
