# from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse

from .models import Person, History

import datetime as datetime2, calendar
from datetime import datetime


# INDEX/HOMEPAGE
@login_required(login_url='login') # Required user to log-in before proceeding to URL
def index(request):
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
	# Render the details page template and pass the person object on it
	return render(request, 'masterlist/details.html', {'person': person})

# DELETE ACTION FOR PERSON DETAILS PAGE
@login_required(login_url='login')
def delete(request, person_id):
	# Retrieve person object through the given url pattern (person_id), otherwise throw 404
	person = get_object_or_404(Person, pk=person_id)
	# Delete the retrieved person
	person.delete()
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
	# Redirect to the person details page
	return HttpResponseRedirect(reverse('details', args=[person.person_id]))

# REGISTER PERSON PAGE
@login_required(login_url='login')
def register_page(request):
	# Render the register person page template
	return render(request, 'masterlist/register.html')

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
	if Person.objects.filter(person_surname=P.person_surname,person_firstname=P.person_firstname).exists():
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
		if History.objects.filter(history_id__startswith=str(year)).exists(): # Check if there are more than one history entry from a given year using the history_id
			# Retrieve the history_id of the latest history entry
			latest_entry = History.objects.filter(history_id__startswith=str(year)).latest('history_id')
			# Get the second portion of the history_id (e.g. the '00001' of '2023-00001'), convert it into an integer and add it by one to get the latest entry number
			latest_entry_number = int(latest_entry.history_id.split('-')[1]) + 1
		# Otherwise, assign 1 as the latest entry number
		else:
			latest_entry_number = 1
		# Create the history entry for the given person
		P.history_set.create(
			# Generate history_id
			history_id = str(year) + '-' + (
				'0000' if latest_entry_number < 10 else
				'000' if latest_entry_number < 100 else
				'00' if latest_entry_number < 1000 else
				'0' if latest_entry_number < 10000 else
				''
			) + str(latest_entry_number),
			# Generate short description
			history_short_desc = firstname + ' ' + surname + ' was successfully registered (' + id + ')',
			# Generate long/detailed description
			history_long_desc = firstname + ' ' + surname + ' was successfully registered and assigned an ID: ' + id + ' on ' + str(calendar.month_name[today.month]) + ' ' + str(today.day) + ', ' + str(today.year) + ' at ' + str(datetime.now().strftime("%I:%M %p")),
			# Generate timestamp (MM-DD-YY HH:MM:SS)
			history_timestamp = str(datetime.now().strftime("%m-%d-%y %H:%M:%S"))
		)
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
	# Render the view history page template and pass all History objects in it
	return render(request, 'masterlist/history.html', {'history': History.objects.all()})