from django.contrib import admin
from .models import *

admin.site.register(Advisor)
admin.site.register(Student)
admin.site.register(Appointment)
admin.site.register(Feedback)
admin.site.register(AdvisingHours)
admin.site.register(Task)
admin.site.register(Notification)