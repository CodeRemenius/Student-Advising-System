from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_student, name='login_student'),
    path('signup/', views.signup_student, name='signup_student'),
    path('profile/', views.view_profile, name='profile_student'),
    path('profile/edit/', views.edit_profile, name='edit_profile_student'),
    path('advisor/select/', views.select_advisor, name='select_advisor'),
    path('appointment/schedule/', views.schedule_appointment, name='schedule_appointment_student'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail_student'),
    path('appointment/history/', views.appointment_history, name='appointment_history_student'),
    path('appointment/<int:appointment_id>/feedback/', views.appointment_feedback, name='appointment_feedback_student'),
    path('notifications/', views.student_notifications, name='student_notifications'),
    path('tasks/', views.view_tasks, name='view_tasks_student'),
    path('dashboard/', views.dashboard_student, name='dashboard_student'),
    path('appointment/view/', views.view_appointments, name='view_appointments_student'),
    path('logout/', views.logout_view, name='logout_student'),
    path('task/history/', views.task_history, name='task_history_student'),
    path('pick-advisor/', views.select_advisor, name='pick_advisor'),
    path('save_advisor/', views.save_advisor, name='save_advisor'),    
    path('tasks/<int:task_id>/complete/', views.mark_task_completed, name='mark_task_completed'),
    path('appointment/view/', views.view_appointments, name='view_appointments_student'),
    path('approved/appointments/', views.approve_appointment, name='approved_appointments_student'),
    path('edit/appointment/<int:appointment_id>/', views.edit_appointment, name='edit_appointment_student'),


]
