from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import History
from .views import create_history_entry

import datetime as datetime2, calendar
from datetime import datetime


# When log-in signal is received (i.e., when User logs in), add a log-in entry to History
@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
	# Generate datetime object
	today = datetime2.date.today()
	# Retrieve current year
	year = today.year
	# Generate history entry
	create_history_entry(
		None,
		f'{user} logged-in to the system',
		f'User \'{user}\' logged-in to the system on ' + str(calendar.month_name[today.month]) + ' ' + str(today.day) + ', ' + str(today.year) + ' at ' + str(datetime.now().strftime("%I:%M %p")),
		'System'
	)

# When log-out signal is received (i.e., when User logs out), add a log-out entry to History
@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    # Generate datetime object
	today = datetime2.date.today()
	# Retrieve current year
	year = today.year
	# Generate history entry
	create_history_entry(
		None,
		f'{user} logged-out from the system',
		f'User \'{user}\' logged-out from the system on ' + str(calendar.month_name[today.month]) + ' ' + str(today.day) + ', ' + str(today.year) + ' at ' + str(datetime.now().strftime("%I:%M %p")),
		'System'
	)
