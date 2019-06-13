#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
You should install TKinter to use this module
"""

import tkinter as tk

class ReportForm(object):
	"""
	GUI-window with 3 widgets - list of tasks, text field with information about tasks
	and button for showing short summury about every task
	"""
	def __init__(self, redmine_data=None):
		super(ReportForm, self).__init__()

		#widgets
		self.root = tk.Tk()
		self.frame_right = tk.LabelFrame(self.root)
		self.frame_left = tk.LabelFrame(self.root, text=u'Tasks')
		self.pad = 10
		self.button_fill_main_text = tk.Button(self.frame_left, text=u"Show summary", width=25, height=5)
		self.main_text = tk.Text(self.frame_right, width=100, height=56, wrap='word')
		self.lbox_tasks = tk.Listbox(self.frame_left, width=25, height=43)
		self.label_for_issue_entry = tk.Label(self.frame_left, text="Task ID", width=5)
		self.issue_entry = tk.Entry(self.frame_left, width=17)

		#packing
		self.frame_left.pack(side='left', padx=self.pad, pady=self.pad)
		self.frame_right.pack(side='left', padx=self.pad, pady=self.pad)
		self.lbox_tasks.pack(padx=self.pad, pady=self.pad)
		self.main_text.pack(padx=self.pad, pady=self.pad)
		self.button_fill_main_text.pack(side='bottom', padx=self.pad, pady=self.pad)
		self.label_for_issue_entry.pack(side='left', padx=self.pad + 5, pady=self.pad)
		self.issue_entry.pack(side='left', padx=self.pad, pady=self.pad)

		#binding events
		self.lbox_tasks.bind('<<ListboxSelect>>', self.lbox_task_select)
		self.issue_entry.bind('<Return>', self.entry_task_select)
		self.button_fill_main_text.bind('<Button-1>', self.text_main_fill_button_click)

		#tie with redmine data
		self.set_redmine_data(redmine_data)

	def set_redmine_data(self, redmine_data):
		self.redmine_data = redmine_data

		self.set_text_main()
		self.set_tasks_list()

	#Text setters
	def set_text_main(self, issue_id='all', mode='short'):
		self.main_text.delete(1.0, 'end')
		if self.redmine_data != None and issue_id != None:
			self.main_text.insert(1.0, self.redmine_data.get_issues_output_text(issue_id=issue_id, mode=mode))

	def set_tasks_list(self):
		self.lbox_tasks.delete(0, 'end')
		if self.redmine_data != None:
			for task in self.redmine_data.get_issues_list():
				self.lbox_tasks.insert('end', task)

	def clear_issue_entry(self):
		self.issue_entry.delete(0, 'end')

	#Events processing
	def lbox_task_select(self, event):
		lbox = event.widget

		if not lbox.curselection():
			return

		index = int(lbox.curselection()[0])
		task_id = lbox.get(index)
		self.set_text_main(issue_id=task_id, mode='full')

	def text_main_fill_button_click(self, event):
		self.set_text_main()
		self.clear_issue_entry()

	def entry_task_select(self, event):
		entry = event.widget
		task_id = entry.get()
		if not task_id.isdigit():
			task_id = None
		else:
			task_id = int(task_id)

		self.set_text_main(issue_id=task_id, mode='full')
