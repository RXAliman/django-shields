# from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse

from .models import Person, History

import datetime as datetime2, calendar
from datetime import datetime


# INDEX/HOMEPAGE
@login_required(login_url='login') # Required user to log-in before proceeding to URL
def index(request):
	# Append a message to the messages processor stating the currently logged-in user
	messages.info(request, '{}, welcome to the SHIELDS!'.format(request.user.username))
	# Render the index page template
	return render(request, 'masterlist/index.html')

# SEARCH RESULTS PAGE
@login_required(login_url='login')
def search_results_page(request):
	# Retrieve search parameters from the index page
	search_filter = request.POST['search-filter']
	search_content = request.POST['search']
	# Storage for search results
	result = []
	# Generate database query from the given search parameters when search filter is by name
	words = search_content.split()
	queries = [Q(person_firstname__icontains=word) |
		Q(person_middlename__icontains=word) |
		Q(person_surname__icontains=word) |
		Q(person_extension__icontains=word) for word in words]
	if search_filter == 'by-name':
		result = Person.objects.filter(*queries).distinct()
	# If otherwise, just do the query according to what's needed
	elif search_filter == 'by-id':
		result = Person.objects.filter(person_id__contains=search_content)
	elif search_filter == 'by-street-no':
		result = Person.objects.filter(person_street_no__contains=search_content)
	elif search_filter == 'by-house-no':
		result = Person.objects.filter(person_house_no__icontains=search_content)
	elif search_filter == 'by-status':
		result = Person.objects.filter(person_status__icontains=search_content)
	# Pass all the needed variables to the template
	context = {
		'search_results': result,
		'search_content': search_content,
		'search_filter': search_filter,
	}
	# Render the search results page template
	return render(request, 'masterlist/search_results.html', context)

# PERSON DETAILS PAGE
@login_required(login_url='login')
def details_page(request, person_id):
	# Retrieve person object through the given url pattern (person_id), otherwise throw 404
	person = get_object_or_404(Person, pk=person_id)
	# Stores the context variables to be passed on to the template
	context = {
		'person': person,
		'history': person.history_set.all().order_by('-history_id'),
	}
	# Render the details page template and pass the person object on it
	return render(request, 'masterlist/details.html', context)

# DELETE ACTION FOR PERSON DETAILS PAGE
@login_required(login_url='login')
def delete(request, person_id):
	# Retrieve person object through the given url pattern (person_id), otherwise throw 404
	person = get_object_or_404(Person, pk=person_id)
	# Retrieve person details for the history deletion entry
	surname = person.person_surname
	firstname = person.person_firstname
	id = person.person_id
	# Generate datetime object
	today = datetime2.date.today()
	# Retrieve current year
	year = today.year
	# Add history entry for the delete action
	create_history_entry(
		person,
		firstname + ' ' + surname + ' was deleted from the database (' + id + ')',
		firstname + ' ' + surname + ' (' + id + ') was deleted from the database on ' + str(calendar.month_name[today.month]) + ' ' + str(today.day) + ', ' + str(today.year) + ' at ' + str(datetime.now().strftime("%I:%M %p")),
		request.user.username
	)
	# Delete the retrieved person
	person.delete()
	# Append a message to be displayed by the message processor
	messages.success(request, 'Successfully deleted from the database')
	# Redirect user to the 'View Masterlist' page
	return HttpResponseRedirect(reverse('view_masterlist'))
	
# EDIT PERSON DETAILS PAGE
@login_required(login_url='login')
def edit_page(request, person_id):
	# Retrieve person object through the given url pattern (person_id), otherwise throw 404
	person = get_object_or_404(Person, pk=person_id)
	# Render the edit page template and pass the person object on it
	return render(request, 'masterlist/edit.html', {'person': person})

# SUBMIT ACTION FOR EDIT PERSON DETAILS PAGE
@login_required(login_url='login')
def submit_edit(request, person_id):
	# Retrieve person object through the given url pattern (person_id), otherwise throw 404
	person = get_object_or_404(Person, pk=person_id)
	# Retrieve the input field values
	surname = request.POST['surname'].title()
	firstname = request.POST['firstname'].title()
	street_no = request.POST['street-no']
	status = request.POST['status']
	# Optional Fields (can be NULL/Empty)
	if request.POST['middlename'] and request.POST['middlename'] != "None":
		middlename = request.POST['middlename'].title()
	else:
		middlename = ''
	if request.POST['extension']:
		extension = request.POST['extension'] 
	else:
		extension = ''
	if request.POST['house-no']:
		house_no = request.POST['house-no']
	else:
		house_no = ''
	# Check if the details are modified, otherwise display a 'no modifications' message
	if (
		person.person_surname == surname and
		person.person_firstname == firstname and
		person.person_middlename == middlename and
		person.person_extension == extension and
		str(person.person_street_no) == street_no and
		person.person_house_no == house_no and
		person.person_status == status
	):
		messages.info(request, 'No changes were made.')
		return HttpResponseRedirect(reverse('details', args=[person_id]))
	# Check if the given person exists, then go back to edit person page if it does
	if Person.objects.exclude(pk=person_id).filter(person_surname=surname,person_firstname=firstname,person_middlename=middlename,person_extension=extension).exists():
		messages.error(request, '{} {} {}already exists in the database...'.format(
			firstname,
			surname,
			(extension + ' ' if extension else '')
		))
		return HttpResponseRedirect(reverse('edit', args=[person_id]))
	# Otherwise, proceed to modification
	else:
		# Generate a datetime object
		today = datetime2.date.today()
		# Retrieve the current year
		year = today.year
		# Generate long description for this modification
		long_description = (
			'Successfully modified the following information of {} {}{}'.format(
				person.person_firstname,
				person.person_surname,
				(' ' + person.person_extension if person.person_extension else '')
			) + ' on ' + str(calendar.month_name[today.month]) + ' ' + str(today.day) + ', ' + str(today.year) + ' at ' + str(datetime.now().strftime("%I:%M %p")) + ':\n' +
			('\tFirst Name: {}\n'.format(firstname) if person.person_firstname != firstname else '') +
			('\tLast Name: {}\n'.format(surname) if person.person_surname != surname else '') +
			('\tDeleted Middle Name\n' if not middlename and middlename != person.person_middlename else '\tMiddle Name: {}\n'.format(middlename) if person.person_middlename != middlename else '') +
			('\tDeleted Extension\n' if not extension and extension != person.person_extension else '\tExtension: {}\n'.format(extension) if person.person_extension != extension else '') +
			('\tStreet Number: {}\n'.format(street_no) if str(person.person_street_no) != street_no else '') +
			('\tDeleted House Number\n' if not house_no and house_no != person.person_house_no else '\tHouse Number: {}\n'.format(house_no) if person.person_house_no != house_no else '') +
			('\tStatus: {}\n'.format(status) if person.person_status != status else '')
		)
		# Create a history entry for this modification
		create_history_entry(
			person,
			'Successfully modified {} {}{}\'s information.'.format(
				person.person_firstname,
				person.person_surname,
				' ' + person.person_extension + '.' if person.person_extension else ''
			),
			long_description,
			request.user.username
		)
		# Track changes
		person.person_surname = surname
		person.person_firstname = firstname
		person.person_middlename = middlename
		person.person_extension = extension
		person.person_street_no = street_no
		person.person_house_no = house_no
		person.person_status = status
		# Save these changes
		person.save()
		# Append a message to the messages processor
		messages.success(request, 'Successfully modified person with ID {}'.format(person_id))
		# Redirect to the person details page
		return HttpResponseRedirect(reverse('details', args=[person.person_id]))

# REGISTER PERSON PAGE
@login_required(login_url='login')
def register_page(request):
	# Render the register person page template
	return render(request, 'masterlist/register.html')

# CREATE HISTORY ENTRY FUNCTION
def create_history_entry(
	person_object,
	short_description,
	long_description,
	user_who_did_it
):
	# Generate datetime object
	today = datetime2.date.today()
	# Retrieve current year
	year = today.year
	# Check if there are more than one history entry from a given year using the history_id
	if History.objects.filter(history_id__startswith=str(year)).exists():
		# Retrieve the history_id of the latest history entry
		latest_entry = History.objects.filter(history_id__startswith=str(year)).latest('history_id')
		# Get the second portion of the history_id (e.g. the '00001' of '2023-00001'), convert it into an integer and add it by one to get the latest entry number
		latest_entry_number = int(latest_entry.history_id.split('-')[1]) + 1
	# Otherwise, assign 1 as the latest entry number
	else:
		latest_entry_number = 1
	# Create the history entry for the given person
	if person_object:
		person_object.history_set.create(
			# Generate history_id
			history_id = str(year) + '-' + (
				'0000' if latest_entry_number < 10 else
				'000' if latest_entry_number < 100 else
				'00' if latest_entry_number < 1000 else
				'0' if latest_entry_number < 10000 else
				''
			) + str(latest_entry_number),
			# Generate short description
			history_short_desc = short_description,
			# Generate long/detailed description
			history_long_desc = long_description,
			# Generate timestamp (MM-DD-YY HH:MM:SS)
			history_timestamp = str(datetime.now().strftime("%m-%d-%y %H:%M:%S")),
			# Add current user to the entry
			history_done_by = user_who_did_it
		)
	# Otherwise let the system the history entry (i.e., for login and logout)
	else:
		History.objects.create(
			# Generate history_id
			history_id = str(year) + '-' + (
				'0000' if latest_entry_number < 10 else
				'000' if latest_entry_number < 100 else
				'00' if latest_entry_number < 1000 else
				'0' if latest_entry_number < 10000 else
				''
			) + str(latest_entry_number),
			# Generate short description
			history_short_desc = short_description,
			# Generate long/detailed description
			history_long_desc = long_description,
			# Generate timestamp (MM-DD-YY HH:MM:SS)
			history_timestamp = str(datetime.now().strftime("%m-%d-%y %H:%M:%S")),
			# Add current user to the entry
			history_done_by = user_who_did_it
		)

# SUBMIT ACTION FOR REGISTER PERSON PAGE
@login_required(login_url='login')
def submit_register(request):
	# Generate a Person object
	P = Person()
	# Required Fields (must not be NULL/Empty)
	surname = request.POST['surname'].title()
	firstname = request.POST['firstname'].title()
	street_no = request.POST['street-no']
	status = request.POST['status']
	# Optional Fields (can be NULL/Empty)
	if request.POST['middlename'] and request.POST['middlename'] != "None":
		P.person_middlename = request.POST['middlename'].title()
	else:
		P.person_middlename = ''
	if request.POST['extension']:
		P.person_extension = request.POST['extension'] 
	else:
		P.person_extension = ''
	if request.POST['house-no']:
		P.person_house_no = request.POST['house-no']
	else:
		P.person_house_no = ''
	# Check if the given person exists, then go back to register person page if it does
	if Person.objects.filter(person_surname=surname,person_firstname=firstname,person_middlename=P.person_middlename,person_extension=P.person_extension).exists():
		messages.error(request, '{} {} {}already exists in the database...'.format(
			firstname,
			surname,
			(P.person_extension + ' ' if P.person_extension else '')
		))
		return HttpResponseRedirect(reverse('register'))
	# Otherwise proceed to registration
	else:
		# Create primary key (1-0001-2023 / Street#-Entry#-Year)
		if Person.objects.filter(person_street_no=street_no).exists(): # Check if any person from a given street exists
			# Retrieve the latest person_id from the given street
			latest_entry = Person.objects.filter(person_street_no=street_no).latest('person_id')
			# Get the second portion of the person_id (for instance, the '0001' from '1-0001-2023'), convert it into an integer and add it by one to get the latest entry number
			latest_entry_number = int(latest_entry.person_id.split('-')[1]) + 1
		# Otherwise, assign 1 as the latest entry number
		else:
			latest_entry_number = 1
		# Generate a datetime object
		today = datetime2.date.today()
		# Retrieve the current year
		year = today.year
		# Format the person_id (#-NNNN-YYYY / 1-0001-2023)
		id = str(street_no) + '-' + (
			'000' if latest_entry_number < 10 else
			'00' if latest_entry_number < 100 else
			'0' if latest_entry_number < 1000 else
			''
		) + str(latest_entry_number) + '-' + str(year)
		# Assign values from the retrieved informations to the generated Person object
		P.person_id = id
		P.person_surname = surname
		P.person_firstname = firstname
		P.person_street_no = street_no
		P.person_status = status
		# Save the Person object in the database
		P.save()
		# Create the data's first history entry
		create_history_entry(
			P,
			firstname + ' ' + surname + ' was successfully registered (' + id + ')',
			firstname + ' ' + surname + ' was successfully registered and assigned an ID: ' + id + ' on ' + str(calendar.month_name[today.month]) + ' ' + str(today.day) + ', ' + str(today.year) + ' at ' + str(datetime.now().strftime("%I:%M %p")),
			request.user.username
		)
		# Append a message to be displayed by the message processor
		messages.success(request, 'Successfully added to the database.')
		# Redirect to the masterlist view
		return HttpResponseRedirect(reverse('view_masterlist'))

# VIEW MASTERLIST PAGE
@login_required(login_url='login')
def view_masterlist(request):
	# Render the view masterlist page template and pass all Person objects in it
	return render(request, 'masterlist/search_results.html', {'search_results': Person.objects.all().order_by('person_street_no','person_surname')})

# VIEW HISTORY PAGE	
@login_required(login_url='login')
def view_history(request):
	# Render the view history page template and pass all History objects in it arranging from latest to oldest
	return render(request, 'masterlist/history.html', {'history': History.objects.all().order_by('-history_id')})

# SEARCH HISTORY PAGE
@login_required(login_url='login')
def search_history(request):
	# Retrieve search content and search filter
	search_filter = request.POST['history-search-filter']
	search_content = request.POST['history-search']
	# Stores search results from query
	results = []
	# Get query from the retrieved search parameters
	if search_filter == 'by-id':
		results = History.objects.all().filter(history_id__icontains=search_content)
	elif search_filter == 'by-description':
		results = History.objects.all().filter(history_short_desc__icontains=search_content)
	else:
		results = History.objects.all().order_by('-history_id')
	# Stores the context variables to be passed onto the templates
	context = {
		'search_filter': search_filter,
		'search_content': search_content,
		'history': results.order_by('-history_id'),
	}
	# Render the view history page along with the context variables
	return render(request, 'masterlist/history.html', context)

# HISTORY DETAILS PAGE
@login_required(login_url='login')
def history_details_page(request, history_id):
	# Retrieve the corresponding history entry, otherwise raise a 404 error
	entry = get_object_or_404(History, pk=history_id)
	# Determine the variables to be passed onto the context processor
	context = {
		'short_description': entry.history_short_desc,
		'long_description': entry.history_long_desc,
		'timestamp': entry.history_timestamp,
		'history_id': entry.history_id,
		'done_by': entry.history_done_by,
	}
	# Render the history details page template and pass the context along it
	return render(request, 'masterlist/history_details.html', context)

# GENERATE CERTIFICATE PAGE
@login_required(login_url='login')
def generate_certificate_page(request, person_id):
	# Retrieve the corresponding person, otherwise raise a 404 error
	person = get_object_or_404(Person, pk=person_id)
	return render(request, 'masterlist/generate_certificate.html', {'person': person})
	
# SUBMIT ACTION FOR GENERATE CERTIFICATE PAGE
@login_required(login_url='login')
def submit_certificate(request, person_id):
	# Retrieve the corresponding person, otherwise raise a 404 error
	person = get_object_or_404(Person, pk=person_id)
	# Generate a datetime object
	today = datetime2.date.today()
	# Retrieve the current year
	year = today.year
	# Retrieve purpose field
	purpose = ('Certification for Meralco Application' if request.POST['purpose'] == 'meralco' else
		'Certification for Manila Water Application' if request.POST['purpose'] == 'manilawater' else
		'Certificate of Residency' if request.POST['purpose'] == 'residency' else
		'Certificate of Membership' if request.POST['purpose' == 'membership'] else '') if request.POST['purpose'] != 'others' else request.POST['other-purpose'].title()
	# Create a history entry for this generation
	create_history_entry(
		person,
		'Created certificate for ' + person.person_firstname + ' ' + person.person_surname + ' (' + person.person_id + ')',
		'Created certificate for ' + person.person_firstname + ' ' + person.person_surname + ' (' + person.person_id + ') on ' + str(calendar.month_name[today.month]) + ' ' + str(today.day) + ', ' + str(today.year) + ' at ' + str(datetime.now().strftime("%I:%M %p")) + ' with the following information:\n' +
		'Type: {}\n'.format(purpose.title()) +
		'Issue Date: {}'.format(request.POST['issuedate']),
		request.user.username
	)
	# Stores the context variables to be passed onto the template system
	context = {
		"first_name": request.POST['first_name'].upper,
		"last_name": request.POST['last_name'].upper,
		"street_number": request.POST['street_number'],
		"date_issued": request.POST['issuedate'],
		"purpose": purpose.upper(),
		"status": request.POST['status'],
		"middlename": request.POST['middlename'].upper,
		"extension": request.POST['extension'].upper,
		"house_number": request.POST['house_number'],
		"history_id": History.objects.all().latest('history_id').history_id,
	}
	# Render the given template along with the context variables
	return render(request, 'masterlist/certificate.html', context)