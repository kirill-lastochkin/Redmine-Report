#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
You should install redminelib
sudo pip install python-redmine
more info you can get from https://python-redmine.com/
"""

from redminelib import Redmine
from redminelib import exceptions
from redminelib import packages
import datetime

class MyIssue(object):
	"""
	Info about issue collected from redmine server.
	If you set @release_used_data to True, after get_output_data_from_raw_data() call
	all raw data will be released
	"""
	def __init__(self, raw_issue, time_spent=0, release_used_data=True):
		super(MyIssue, self).__init__()
		self.raw_issue = raw_issue
		self.time_spent = time_spent
		self.release_used_data = release_used_data
		self.output_data_prepared = False
		self.activity_list = []

	def add_spent_time(self, time_spent):
		self.time_spent += time_spent

	def get_spent_time(self):
		return self.time_spent

	def add_activity(self, activity):
		self.activity_list.append(activity)

	def get_output_data_from_raw_data(self, key_words):
		self._get_main_activity()
		self._get_issue_work_status()
		self._get_issue_task_group(key_words)
		self._prepare_description()
		self.output_data_prepared = True

		if self.release_used_data == True:
			del self.raw_issue

	def _get_main_activity(self):
		self.main_activity = 'Some test or management work'
		for activity in list(set(self.activity_list)):
			if activity == 'Code':
				self.main_activity = activity
				break
			if activity == 'Discuss' and len(self.activity_list) == 1:
				self.main_activity = activity
				break

		if self.release_used_data == True:
			del self.activity_list

	def _get_issue_work_status(self):
		status = self.raw_issue.status.name
		if status == 'In Progress' or status == 'Re-opened' or status == 'New':
			self.work_status = 'In Progress'
		elif status == 'Pending' or status == 'Testing':
			self.work_status = 'Waiting'
		else:
			self.work_status = 'Done'

	def _get_issue_task_group(self, key_words):
		"""Marking issues according to given key-words"""
		self.task_group = 'unsorted'
		if key_words == None:
			return

		for key in key_words.keys():
			for word in key_words[key]:
				search_str = self.raw_issue.subject.lower()
				if search_str.find(word) != -1:
					self.task_group = key
					break

	def _prepare_description(self):
		self.theme = self.raw_issue.subject.encode('utf-8')
		self.comments = []

		for journal in self.raw_issue.journals:
			if hasattr(journal, 'notes'):
				self.comments.append((journal.user.name, journal.created_on, journal.notes))

class MyRedmineData(object):
	"""
	Object produced by this class makes connection with redmine-server using @url and @api_key
	"""
	def __init__(self, url, api_key):
		super(MyRedmineData, self).__init__()

		if not isinstance(url, basestring) or not isinstance(api_key, basestring):
			print "\nURL and API key must be strings\n".format(url)
			raise WrongRedmineParamError

		self.redmine_entity = Redmine(url, key=api_key)

		try:
			self.user = self.redmine_entity.user.get('current')
		except exceptions.AuthError:
			print "\nBad API key {}\n".format(api_key)
			raise WrongRedmineParamError
		except packages.requests.exceptions.ConnectionError:
			print "\nBad URL {}\n".format(url)
			raise WrongRedmineParamError

		self.raw_data_collected = False
		self.issues = {}

	def get_user_active_issues(self, start_date, end_date=datetime.datetime.now()):
		"""
		Get and store raw data from redmine-server about all issues for period
		with time calculating for each issue
		"""
		self.issues.clear()
		for time_entry in self.user.time_entries:
			if start_date.date() <= time_entry.spent_on <= end_date.date():
				time_spent = float(time_entry.hours)
				issue_id = time_entry.issue.id
				try:
					self.issues[issue_id].add_spent_time(time_spent)
				except KeyError:
					raw_issue = self.redmine_entity.issue.get(issue_id, include=['journals'])
					self.issues[issue_id] = MyIssue(raw_issue, time_spent)

				self.issues[issue_id].add_activity(time_entry.activity.name)

		self.raw_data_collected = True

	def get_issues_list(self):
		"""
		Get list of issues IDs, collected on get_user_active_issues() call
		"""
		assert self.raw_data_collected

		self.issues_list = []

		for issue_id in self.issues.keys():
			self.issues_list.append(issue_id)

		return self.issues_list

	def prepare_active_issues_output_data(self, key_words=None):
		"""
		Goes through issues list and prepares output data for each issue
		"""
		assert self.raw_data_collected

		self.total_time_spent = 0.0

		for issue_id in self.issues.keys():
			issue_entry = self.issues[issue_id]
			issue_entry.get_output_data_from_raw_data(key_words)
			self.total_time_spent += issue_entry.get_spent_time()

	def get_issues_output_text(self, issue_id='all', mode='short'):
		"""
		Get text, ready to be printed in report.
		@issue could be 'all' for all issues or single ID
		@mode is
		  - 'short' - info without comments
		  - 'full'  - all collected info
		"""
		assert self.raw_data_collected

		text = u""

		if issue_id == 'all':
			text += u"Всего затрачено " + str(self.total_time_spent) + u" часов\n\n"

		for issue_idx in self.issues.keys():
			if issue_id != 'all' and issue_id != issue_idx:
				continue

			issue = self.issues[issue_idx]
			assert issue.output_data_prepared

			text += u"Задача " + str(issue_idx) + u"\nТема " + issue.theme.decode('utf-8') + u"\nСтатус: " + issue.work_status + u"\nГруппа: " + issue.task_group + \
			        u"\nЗатрачено часов: " + str(issue.get_spent_time()) + u"\nОсновной вид работ: " + issue.main_activity

			if mode == 'full':
				for comment in issue.comments:
					if comment[0].find("Jenkins") != -1 or not comment[2]:
						continue

					text += "\n\n" + comment[0] + " " + str(comment[1]) + "\n" + comment[2] + "\n"

			text += "\n\n"

		return text

def set_start_date(**kwargs):
	"""
	use @delta to set start date as current date minus delta (in days)
	use @year, @month, @day for explicitly start date setting
	"""
	cur_date = datetime.datetime.now()

	if len(kwargs) == 1:
		delta = kwargs['delta']
		if delta <= 0:
			raise WrongStartDateError

		time_delta = datetime.timedelta(days=delta)
		return cur_date - time_delta
	else:
		year_from = kwargs['year']
		month_from = kwargs['month']
		day_from = kwargs['day']
		start_date = datetime.datetime(year=year_from, month=month_from, day=day_from)

		if start_date > cur_date:
			raise WrongStartDateError

		return start_date


class WrongStartDateError(Exception):
	pass

class WrongRedmineParamError(Exception):
	pass