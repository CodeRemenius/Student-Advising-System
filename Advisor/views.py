from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import *
from .backends import EmailBackend 



def login_advisor(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Authenticate user
        user = EmailBackend().checked(request, email=email, password=password)
        
        if user is not None:
            # Check if the authenticated user is an advisor
            if Advisor.objects.filter(user=user).exists():
                auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect('dashboard_advisor')  # Redirect to advisor dashboard
            else:
                return render(request, 'login.html', {'error_message':'You are not authorized to access this page.'})
        else:
            return render(request, 'login.html', {'error_message':'Invalid email or password.'})

    return render(request, 'login.html')

def signup_advisor(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        areas_of_expertise = request.POST['areas_of_expertise']
        
        # Check if a user with the same first name and last name already exists
        existing_user = User.objects.filter(first_name=first_name, last_name=last_name).exists()
        if existing_user:
            return render(request, 'signup.html', {'error_message': 'User with this first name and last name already exists.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_message': 'Email already exists. Please use a different email.'})
        
        if Advisor.objects.filter(phone_number=phone_number).exists():
            return render(request, 'signup.html', {'error_message': 'Phone number already exists. Please use a different phone number.'})

        # Combine first name and last name to create username
        username = f"{first_name} {last_name}"
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        
        # Create advisor
        advisor = Advisor.objects.create(user=user, email=email, phone_number=phone_number, areas_of_expertise=areas_of_expertise)
        
        # Redirect to login page
        return redirect('login_advisor')
    else:
        return render(request, 'signup.html')
        
def dashboard_advisor(request):
    last_4_tasks = Task.objects.filter(advisor=request.user.advisor).order_by('-deadline')[:4]
    
    # Filter appointments where both advisor and student have approved
    next_4_appointments = Appointment.objects.filter(
        advisor=request.user.advisor, 
        approved_by_advisor=True, 
        approved_by_student=True
    ).order_by('start_time')[:4]
    
    # Filter appointments where student has approved but advisor has not
    last_3_unapproved_appointments = Appointment.objects.filter(
        advisor=request.user.advisor,
        approved_by_student=True,
        approved_by_advisor=False
    ).order_by('-start_time')[:3]
    
    context = {
        'last_4_tasks': last_4_tasks,
        'next_4_appointments': next_4_appointments,
        'last_3_unapproved_appointments': last_3_unapproved_appointments
    }
    
    return render(request, 'dashboard_advisor.html', context)

def view_profile(request):
    # Retrieve the current user's profile information
    user = request.user

    # Pass the profile information to the template
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)

def edit_profile(request):
    user = request.user
    advisor = Advisor.objects.get(user=user)
    context = {
        'user': user,
    }

    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        areas_of_expertise = request.POST.get('areas_of_expertise')
        
        # Update user's profile information
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Update advisor's profile information
        advisor.phone_number = phone_number
        advisor.areas_of_expertise = areas_of_expertise
        advisor.save()

        # Redirect to view profile page
        return redirect('profile_advisor')

    return render(request, 'edit_profile.html', context)

@login_required
def schedule_appointment(request):
    advisor = request.user.advisor
    students = Student.objects.filter(advisor=advisor)

    if request.method == 'POST':
        student_id = request.POST.get('student')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        topic = request.POST.get('topic')
        mode_of_meeting = request.POST.get('mode_of_meeting')

        # Convert start_time and end_time strings to datetime objects
        start_time = timezone.make_aware(datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M'))
        end_time = timezone.make_aware(datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M'))

        # Create the appointment
        appointment = Appointment.objects.create(
            advisor=advisor,
            student_id=student_id,
            start_time=start_time,
            end_time=end_time,
            topic=topic,
            mode_of_meeting=mode_of_meeting,
            approved_by_advisor=True  # Automatically approved by advisor
        )

        # Create a notification for the student
        student_user = Student.objects.get(pk=student_id).user
        message = "An appointment has been scheduled by your advisor. Look into it now."
        Notification.objects.create(user=student_user, message=message)

        # Redirect to appointment detail page or any other page as needed
        return redirect('appointment_detail', appointment_id=appointment.id)

    return render(request, 'schedule_appointment.html', {'students': students})

def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, 'appointment_detail.html', {'appointment': appointment})

def appointment_history(request):
    appointments = Appointment.objects.filter(advisor=request.user.advisor, is_completed=True) | Appointment.objects.filter(advisor=request.user.advisor, is_rejected=True)
    return render(request, 'appointment_history.html', {'appointments': appointments})

def appointment_feedback(request):
    feedbacks = Feedback.objects.filter(appointment__advisor=request.user.advisor)
    return render(request, 'appointment_feedback.html', {'feedbacks': feedbacks})

def define_advising_hours(request):
    user = request.user
    advisor = Advisor.objects.get(user=user)
    
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        # Update advisor's advising hours
        advisor.office_hours_start = start_time
        advisor.office_hours_end = end_time
        advisor.save()

        # Redirect to dashboard or any other page
        return redirect('dashboard_advisor')
    
    # Pass the current advising hours to the template
    context = {
        'advisor': advisor,
    }
    return render(request, 'define_advising_hours.html', context)

def view_students(request):
    students = Student.objects.filter(advisor=request.user.advisor)
    return render(request, 'view_students.html', {'students': students})

def assign_task(request):
    advisor = request.user.advisor
    students = Student.objects.filter(advisor=advisor)

    if request.method == 'POST':
        student_id = request.POST.get('student')
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        
        advisor = request.user.advisor  # Current advisor
        
        # Format deadline as datetime object
        deadline = timezone.make_aware(datetime.strptime(deadline, '%Y-%m-%dT%H:%M'))
        
        # Create task
        task = Task.objects.create(advisor=advisor, student_id=student_id, title=title, description=description, deadline=deadline)
        
        # Create notification for the student
        student_user = task.student.user
        message = "You have a new task. Please duly observe and meet the deadline."
        Notification.objects.create(user=student_user, message=message)

        return redirect('task_history') 

    return render(request, 'assign_task.html', {'students': students})

def advisor_notifications(request):
    # Retrieve notifications for the current advisor
    advisor_notifications = Notification.objects.filter(user=request.user)
    context = {
        'notifications': advisor_notifications
    }
    return render(request, 'notifications.html', context)

def student_profile(request, student_id):
    # Retrieve the student object
    student = get_object_or_404(Student, pk=student_id)
    context = {
        'student': student
    }
    return render(request, 'student_profile.html', context)

def task_history(request):
    task_history = Task.objects.filter(advisor=request.user.advisor)
    return render(request, 'task_history.html', {'task_history': task_history})


def view_appointments(request):
    appointments = Appointment.objects.filter(advisor=request.user.advisor, approved_by_advisor=False, is_completed=False, is_rejected=False)
    return render(request, 'view_appointments.html', {'appointments': appointments})

def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.approved_by_advisor = True
    appointment.save()

    # Create notification for the student
    student_user = appointment.student.user
    message = "Your appointment has been approved. Check your appointments."
    Notification.objects.create(user=student_user, message=message)

    return redirect('approved_appointments')

def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        topic = request.POST.get('topic')
        mode_of_meeting = request.POST.get('mode_of_meeting')

        # Update appointment details
        appointment.start_time = start_time
        appointment.end_time = end_time
        appointment.topic = topic
        appointment.mode_of_meeting = mode_of_meeting
        appointment.approved_by_student = False
        appointment.approved_by_advisor = True
        appointment.save()

        # Create notification for the student
        student_user = appointment.student.user
        message = "I have proposed another appointment. Check it and return feedback as soon as possible."
        Notification.objects.create(user=student_user, message=message)

        return redirect('view_appointments')
    else:
        return render(request, 'edit_appointment.html', {'appointment': appointment})

def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.is_rejected = True
    appointment.save()

    # Create notification for the student
    student_user = appointment.student.user
    message = "Your appointment has been rejected. Please reschedule."
    Notification.objects.create(user=student_user, message=message)

    return redirect('view_appointments')

def approved_appointments(request):
    appointments = Appointment.objects.filter(advisor=request.user.advisor, approved_by_advisor=True, approved_by_student=True)
    return render(request, 'approved_appointments.html', {'appointments': appointments})

def complete_appointment(request, appointment_id):
    appointment = Appointment.objects.get(pk=appointment_id)
    appointment.is_completed = True
    appointment.save()
    return redirect('approved_appointments')

def logout_view(request):
    logout(request)
    return redirect('login_advisor')