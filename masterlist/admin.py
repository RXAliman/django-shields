from django.contrib import admin

# Register your models here.
from .models import Person, History


# Connect both Person & History models to the admin site
admin.site.register(Person)
admin.site.register(History)