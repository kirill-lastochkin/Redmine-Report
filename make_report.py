#!/usr/bin/env python
# -*- coding: utf-8 -*-

import myredmine as red
import reportform as rf

#user args
api_key = 'd0550273e53b4887dbaf2dad27c401eec8553078'
redmine_url = 'http://red.eltex.loc'

key_words = {'mpls':['pw', 'mpls', 'rsvp', 'sldf', 'ldp', 'l3vpn'],
             'multicast':['multicast', 'pim', 'msd', u'мультикаст'],
             'ipv6':['ipv6']}

def main():
	start_date = red.set_start_date(year=2019, month=04, day=29)
	my_red = red.MyRedmineData(redmine_url, api_key)
	my_red.get_user_active_issues(start_date)
	my_red.prepare_active_issues_output_data(key_words)

	report = rf.ReportForm(redmine_data=my_red)
	report.root.mainloop()


if __name__ == '__main__':
	main()
