from django.contrib import admin
from .models import Burger, Feedback, UserProfile

admin.site.register(Burger)
admin.site.register(Feedback)
admin.site.register(UserProfile)
