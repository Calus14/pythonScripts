import praw

#tells reddit what your doing
r = praw.Reddit("Just saying hi")
#put username and login here
r.login("calus11", "doubleback2");

#limit is how many threads you want to pull from
#subreddit is the subreddit you want to pull from
top25 = r.get_subreddit("smashbros").get_top(limit=75)

redditors = []
previousRedditors = []

prevFile = open("sentUsers.txt", 'r')

for line in prevFile:
    line.rstrip()
    previousRedditors.append(line)

prevFile.close()

print("Made it here1")
for submission in top25:
    submission.replace_more_comments(limit=16, threshold=10)
    comments = praw.helpers.flatten_tree(submission.comments)
    for comment in comments:
        if comment.author is None:
            continue
        if (comment.author.name not in previousRedditors): 
            print(comment.author.name);
            redditors.append(comment.author.name)

#this is the subject of your message
subject = "I like your dick "
#this is the actuall message itself
msg = "please fuck my wife"

myFile = open("sentUsers.txt", 'a')

print("Made it here")

count = 0
#change this number for the messages to send
messagesToSend = 1000;
for redditor in redditors:
    r.send_message(redditor, subject, msg)
    myFile.write(redditor+"\n")
    count = count + 1
    if count == messagesToSend:
        break

print("We have sent "+count+" messages");

myFile.close()
