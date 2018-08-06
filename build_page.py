from github import Github
import datetime
import operator

# create a username dictionary 
class user_class:
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
	user_stats = dict()
	for u in users: 
		user_stats[u.login] = user_class(u)
	return user_stats

def write_readme_file(user_stats):
	winner = sorted(user_stats.values(), key=operator.attrgetter('total_points'), reverse=True)[0]
	f = open("README.md", "w")

	table_string = """
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

def get_user_stats(passwd):
	# set the time range 
	today = datetime.datetime.today()
	last_week = today - datetime.timedelta(weeks=1)

	# using username and password
	g = Github("agnwinds",passwd)

	# get the repo object
	repo = g.get_user().get_repo("python")

	# get all the issues
	issues = repo.get_issues(state="all", since=last_week)

	# get all the users 
	users = repo.get_collaborators()
	user_stats = create_user_dict(users)

	for i in issues:
		print (i.number)
		if i.closed_by != None:
			user_closed = i.closed_by.login
			print (user_closed)
			user_stats[user_closed].issues_closed += 1
			user_stats[user_closed].total_points += 2

		user_opened = i.user.login 
		user_stats[user_opened].issues_opened += 1
		user_stats[user_opened].total_points += 1

	return (user_stats)


if __name__ == "__main__":
	org_name = "agnwinds"
	passwd = input("Enter password for {}:".format(org_name))
	user_stats = get_user_stats(passwd)
	write_readme_file(user_stats)
