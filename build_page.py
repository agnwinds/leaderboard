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

POINTS_PER_CLOSE = 2
POINTS_PER_OPEN = 1

# create a username class to store statistics for each user 
class UserClass:
	def __init__(self, u):
		self.issues_closed = 0
		self.issues_opened = 0
		self.commits = 0
		self.additions = 0
		self.deletions = 0
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
### Scoring System
2 points per issue closed, 1 per issue opened.

### This Weeks Champion:

|:---:|:----:|:-------:|:-------:|
|<img src="{}" width="60" height="60" /> | [{}](https://github.com/{}) | {} | <img src="img/trophy.jpg" width="60" height="60" />|

|     |   User   |Issues Closed|Issues Opened|
|:---:|:--------:|:-----------:|:-----------:|
""".format(winner.user.avatar_url, winner.user.login, winner.user.login, winner.total_points)
	f.write(table_string)

	# write the sorted list and statistics into a table in markdown format
	for u in (sorted(user_stats.values(), key=operator.attrgetter('total_points'), reverse=True)): 
		image_html = '<img src="{}" width="60" height="60" />'.format(u.user.avatar_url)
		f.write("|{}| [{}](https://github.com/{})| {} | {} |\n".format(image_html, 
			    u.user.login, u.user.login, user_stats[u.user.login].issues_closed, 
			    user_stats[u.user.login].issues_opened))
	f.close()

def get_user_stats(org_name, repo_name, passwd):
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

	# using username and password
	g = Github(org_name, passwd)

	# get the repo object
	repo = g.get_user().get_repo(repo_name)

	# get all the issues
	issues = repo.get_issues(state="all", since=last_week)

	# get all the users 
	users = repo.get_collaborators()
	user_stats = create_user_dict(users)

	# loop over the issues and increment counters for each user
	for i in issues:
		if i.closed_by != None:
			user_closed = i.closed_by.login
			user_stats[user_closed].issues_closed += 1
			user_stats[user_closed].total_points += POINTS_PER_CLOSE

		user_opened = i.user.login 
		user_stats[user_opened].issues_opened += 1
		user_stats[user_opened].total_points += POINTS_PER_OPEN

	return (user_stats)


if __name__ == "__main__":

	if len(sys.argv) > 1:
		# get cmd line info
		org_name = sys.argv[1]
		repo_name = sys.argv[2]

		passwd = sys.argv[3]
#		passwd = input("Enter password for {}:".format(org_name))
		user_stats = get_user_stats(org_name, repo_name, passwd)
		write_readme_file(user_stats)
	else:
		print (__doc__)
