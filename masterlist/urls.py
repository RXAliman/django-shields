from django.urls import path

from . import views


urlpatterns = [
	# Homepage
	path('', views.index, name='index'),
	# Search Results
	path('search/', views.search_results_page, name='search_results'),
	# Details Page
	path('<person_id>', views.details_page, name='details'),
	# Delete Action for Details Page
	path('<person_id>/delete', views.delete, name='delete'),
	# Edit Page
	path('<person_id>/edit', views.edit_page, name='edit'),
	# Submit Action for Edit Page
	path('<person_id>/edit/apply_changes', views.submit_edit, name='submit_edit'),
	# Register Page
	path('register/', views.register_page, name='register'),
	# Submit Action for Register Page
	path('register/submit/', views.submit_register, name='submit_register'),
	# View Masterlist Page
	path('search_for_all/', views.view_masterlist, name='view_masterlist'),
	# View History Page
	path('history/', views.view_history, name='view_history'),
	# Search History Results
	path('history/search/', views.search_history, name='search_history'),
	# History Details Page
	path('history/<history_id>', views.history_details_page, name='history_details'),
	# Generate Certificate Page
	path('<person_id>/generate', views.generate_certificate_page, name='generate'),
	# Submit Action for Generate Certificate Page
	path('<person_id>/generate/processed', views.submit_certificate, name='submit_certificate'),
]