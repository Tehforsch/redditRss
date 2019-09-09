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

def readTopPosts(subredditName, numPosts, minUpvotes, filters):
    submissions = [submission for submission in list(reddit.subreddit(subredditName).top(limit=numPosts*10, time_filter="day"))]
    if filters != []:
        submissions = [submission for submission in submissions if not any(flairToFilter.lower() in submission.link_flair_text.lower() for flairToFilter in filters)]
    submissions = [sub for sub in submissions if getScore(sub) >= minUpvotes]
    return submissions[:numPosts]

def getScore(submission):
    if submission.is_self:
        return submission.score * 20
    else:
        return submission.score

def generateRss(submissions, outputFile, title, description, link, _id):
    feedGen = FeedGenerator()
    feedGen.id(_id)
    feedGen.title(title)
    feedGen.link({"href":link})
    feedGen.description(description)
    for submission in submissions:
        feedItem = feedGen.add_entry()
        submissionItem(feedItem, submission)
    try:
        feedGen.rss_str(pretty=True)
    except ValueError:
        return
    feedGen.rss_file(outputFile)
    
def submissionItem(feedEntry, submission):
    feedEntry.title(submission.title)
    feedEntry.id(submission.url + "/")
    feedEntry.link({"href":submission.shortlink})
    feedEntry.description(getDescription(submission))

def getDescription(submission):
    description = submission.selftext
    if not submission.is_self:
        description = description + "<img src=\"{url}\"><br><a href=\"{url}\">".format(url=submission.url)
    return description

def generateSubredditRss(subredditName, numPosts, minUpvotes, filters):
    generateRss(
            submissions=readTopPosts(subredditName, numPosts, minUpvotes, filters),
            outputFile="feeds/{}.xml".format(subredditName),
            title="{}".format(subredditName),
            description="Top posts {}".format(subredditName),
            link="reddit.com/r/{}/top".format(subredditName),
            _id="reddit.com/r/{}/top".format(subredditName)
            )

def generateMultiSubredditRss(subreddits):
    submissions = []
    name = ""
    for (subreddit, numPosts, filters) in subreddits:
        submissions = submissions + readTopPosts(subreddit, numPosts, filters)
        name = name + subreddit + "+"
    name = name[:-1]

    generateRss(
            submissions=submissions,
            outputFile="feeds/{}.xml".format(name),
            title="Top posts {}".format(name),
            description="Top posts {}".format(name),
            link="reddit.com/r/{}/top".format(name),
            _id="reddit.com/r/{}/top".format(name)
            )

def getSubredditList():
    with open("subreddits", "r") as f:
        for l in f.readlines():
            name, numPosts, minUpvotes, *filters = l.replace("\n", "").split()
            numPosts = int(numPosts)
            minUpvotes = int(minUpvotes)
            yield (name, numPosts, minUpvotes, filters)

for (subreddit, numPosts, minUpvotes, *filters) in getSubredditList():
    generateSubredditRss(subreddit, numPosts, minUpvotes, *filters)
