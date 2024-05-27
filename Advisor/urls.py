from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('login/', views.login_advisor, name='login_advisor'),
    path('signup/', views.signup_advisor, name='signup_advisor'),
    path('dashboard/', views.dashboard_advisor, name='dashboard_advisor'),
    path('profile/', views.view_profile, name='profile_advisor'),
    path('profile/edit/', views.edit_profile, name='edit_profile_advisor'),
    path('appointment/schedule/', views.schedule_appointment, name='schedule_appointment'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/history/', views.appointment_history, name='appointment_history'),
    path('appointment/feedback/', views.appointment_feedback, name='appointment_feedback'),
    path('advising_hours/define/', views.define_advising_hours, name='define_advising_hours'),
    path('students/', views.view_students, name='view_students'),
    path('notifications/', views.advisor_notifications, name='advisor_notifications'),
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('task/assign/', views.assign_task, name='assign_task'),
    # Additional URLs for dashboard
    path('task/history/', views.task_history, name='task_history'),
    path('appointment/view/', views.view_appointments, name='view_appointments'),
    path('approved/appointments/<int:appointment_id>/', views.approve_appointment, name='approved_appointments'),
    path('reject/appointment/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('edit/appointment/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('logout/', views.logout_view, name='logout_advisor'),
    path('approved/appointments/', views.approved_appointments, name='approved_appointments'),
    path('complete/appointment/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
]
