'''
	build_page.py

	Build a markdown file of issue statistic for a github repository

	Usage:
		python build_page.py [user_name] [repo_name]

	Dependencies:
		PyGithub: https://github.com/PyGithub/PyGithub
'''
from github import Github
import datetime
import operator
import sys
# Authentication is defined via github.Auth
from github import Auth

POINTS_PER_CLOSE = 20
POINTS_PER_OPEN = 10
POINTS_PER_PULL = 5
POINTS_PER_COMMIT = 1

# create a username class to store statistics for each user 
class UserClass:
	def __init__(self, u):
		self.issues_closed = 0
		self.issues_opened = 0
		self.commits = 0
		self.additions = 0
		self.deletions = 0
		self.pulls_opened = 0
		self.pulls = 0
		self.user = u
		self.total_points = 0

def create_user_dict(users):
	'''
	Create a dictionary of keys corresponding
	to user logins and values corresponding to
	relevant UserClass instances

	Parameters:
		users  		users object from PyGithub
					contains base info on repo collabs built from 
					repo.get_collaborators()
	Returns:
		user_stats 	UserClass object 
	'''
	user_stats = dict()
	for u in users: 
		if u.login != "agnwinds":
			user_stats[u.login] = UserClass(u)
	return user_stats

def write_readme_file(user_stats):
	'''
	Write the information to the file README.md which 
	can then be built into html by github pages

	Parameters:
		user_stats  	UserClass object 
						contains statistics and base info on repo collabs
	'''
	winner = sorted(user_stats.values(), key=operator.attrgetter('total_points'), reverse=True)[0]
	f = open("README.md", "w")

	table_string = """
	
### This Weeks Champion:

<img src="img/trophy.jpg" width="60" height="60" /> <img src="{}" width="60" height="60" /> [{}](https://github.com/{}) 

**Scoring System:** 
20 points per issue closed. 10 per issue opened. 5 per pull request. 1 per commit to upstream/dev.

|     |   User   |Issues Closed|Issues Opened|Pull Requests| Commits | Points |
|:---:|:--------:|:-----------:|:-----------:|:-----------:|:-------:|:-------:|
""".format(winner.user.avatar_url, winner.user.login, winner.user.login, winner.total_points)
	f.write(table_string)

	# write the sorted list and statistics into a table in markdown format
	for u in (sorted(user_stats.values(), key=operator.attrgetter('total_points'), reverse=True)): 
		image_html = '<img src="{}" width="60" height="60" />'.format(u.user.avatar_url)
		f.write("| {} | [{}](https://github.com/{}) | {} | {} | {} | {} | {} |\n".format(image_html, 
			    u.user.login, u.user.login, user_stats[u.user.login].issues_closed, 
			    user_stats[u.user.login].issues_opened, user_stats[u.user.login].pulls_opened, 
			    user_stats[u.user.login].commits, user_stats[u.user.login].total_points))
	f.close()

def get_user_stats(org_name, repo_name, token):
	'''
	Get the user statistics for a repository repo_name 
	hosted by org_name with passwd

	Returns:
		user_stats  	UserClass object 
						contains statistics and base info on repo collabs
	'''	

	# set the time range 
	today = datetime.datetime.today()
	last_week = today - datetime.timedelta(weeks=1)

	auth = Auth.Token(token)

	# using username and password
	g = Github(auth=auth)

	# get the repo object
	repo = repo = g.get_user(org_name).get_repo(repo_name)

	# get all the issues
	issues = repo.get_issues(state="all", since=last_week)

	# get all the users 
	users = repo.get_collaborators()
	user_stats = create_user_dict(users)

	print ([u for u in users])

	# loop over the issues and increment counters for each user
	for i in issues:

		if i.pull_request != None:
			user_opened = i.user.login 
			if user_opened in user_stats.keys():
				user_stats[user_opened].pulls_opened += 1
				user_stats[user_opened].total_points += POINTS_PER_PULL

		else:
			if i.closed_by != None:
				user_closed = i.closed_by.login
				if user_closed in user_stats.keys():
					user_stats[user_closed].issues_closed += 1
					user_stats[user_closed].total_points += POINTS_PER_CLOSE

			user_opened = i.user.login 
			print (user_stats.keys())
			if user_opened in user_stats.keys():
				user_stats[user_opened].issues_opened += 1
				user_stats[user_opened].total_points += POINTS_PER_OPEN

	# now gather the commit stats
	commits = repo.get_commits(since=last_week)
	for c in commits:
		user_opened = c.committer.login 
		# check it's not a merge commit or something
		if user_opened != "web-flow": 
			try:	
				user_stats[user_opened].commits += 1
				user_stats[user_opened].total_points += POINTS_PER_COMMIT
			except KeyError:
				print("KeyError for committer {}".format(user_opened))

	return (user_stats)


if __name__ == "__main__":

	if len(sys.argv) > 1:
		# get cmd line info
		org_name = sys.argv[1]
		repo_name = sys.argv[2]

		token = sys.argv[3]
#		passwd = input("Enter password for {}:".format(org_name))
		user_stats = get_user_stats(org_name, repo_name, token)
		write_readme_file(user_stats)
	else:
		print (__doc__)
