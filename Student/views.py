from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from Advisor.models import *
from Advisor.backends import EmailBackend 
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_student(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = EmailBackend().checked(request, email=email, password=password)
        
        if user is not None:
            # Check if the authenticated user is a student
            if hasattr(user, 'student'):
                auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect('dashboard_student')  # Redirect to student dashboard
            else:
                return render(request, 'login_student.html', {'error_message': 'You are not authorized to access this page.'})
        else:
            return render(request, 'login_student.html', {'error_message': 'Invalid email or password.'})

    return render(request, 'login_student.html')

def signup_student(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        phone_number = request.POST['phone_number']
        department = request.POST['department']

        # Check if username already exists
        username = f"{first_name} {last_name}"
        if User.objects.filter(username=username).exists():
            error_message = "Username already exists. Please choose a different combination of first name and last name."
            return render(request, 'student_signup.html', {'error_message': error_message})

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            error_message = "Email already exists. Please use a different email."
            return render(request, 'student_signup.html', {'error_message': error_message})

        # Check if phone number already exists
        if Student.objects.filter(phone_number=phone_number).exists():
            error_message = "Phone number already exists. Please use a different phone number."
            return render(request, 'student_signup.html', {'error_message': error_message})

        # Create User and Student objects
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        student = Student.objects.create(user=user, email=email, phone_number=phone_number, department=department)

        # Redirect to login page
        return redirect('login_student')
    else:
        return render(request, 'student_signup.html')

def dashboard_student(request):
    # Fetch upcoming appointments sorted by start time and limited to the next 4
    upcoming_appointments = Appointment.objects.filter(
        student=request.user.student,
        approved_by_advisor=True,
        approved_by_student=True,
        is_completed=False,
        is_rejected=False,
        start_time__gte=timezone.now()
    ).order_by('start_time')[:4]
    
    # Fetch the last 4 uncompleted tasks for the student
    tasks = Task.objects.filter(
        student=request.user.student,
        completed=False,
        failed=False
    ).order_by('-deadline')[:4]

    # Fetch appointments awaiting approval where approved_by_student is False
    awaiting_approval_appointments = Appointment.objects.filter(
        student=request.user.student,
        approved_by_student=False
    )

    # If the student doesn't have an advisor, fetch advisors to populate the select field in the modal
    if not request.user.student.advisor:
        advisors = Advisor.objects.all()
        return render(request, 'dashboard_student.html', {
            'upcoming_appointments': upcoming_appointments,
            'tasks': tasks,
            'awaiting_approval_appointments': awaiting_approval_appointments,
            'advisors': advisors
        })
    else:
        return render(request, 'dashboard_student.html', {
            'upcoming_appointments': upcoming_appointments,
            'tasks': tasks,
            'awaiting_approval_appointments': awaiting_approval_appointments
        })

def save_advisor(request):
    if request.method == 'POST':
        advisor_id = request.POST.get('advisor')
        advisor = Advisor.objects.get(pk=advisor_id)
        student = request.user.student
        student.advisor = advisor
        student.save()
    return redirect('dashboard_student')

def view_profile(request):
    return render(request, 'profile_students.html')

def edit_profile(request):
    user = request.user
    student = Student.objects.get(user=user)
    context = {
        'user': user,
    }

    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        department = request.POST.get('department')
        
        # Update user's profile information
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Update advisor's profile information
        student.phone_number = phone_number
        student.department = department
        student.save()

        # Redirect to view profile page
        return redirect('profile_student')

    return render(request, 'edit_profile_students.html', context)

def select_advisor(request):
    advisors = Advisor.objects.all()
    current_advisor = request.user.student.advisor

    if request.method == 'POST':
        advisor_id = request.POST.get('advisor')
        student = request.user.student
        advisor = Advisor.objects.get(pk=advisor_id)
        student.advisor = advisor
        student.save()
        return redirect('dashboard_student')

    return render(request, 'select_advisor.html', {'advisors': advisors, 'current_advisor': current_advisor})

def schedule_appointment(request):
    student = request.user.student
    advisor = student.advisor
    error_message = ""  # Initialize error message

    if request.method == 'POST':
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        topic = request.POST.get('topic')
        mode_of_meeting = request.POST.get('mode_of_meeting')

        # Convert start_time and end_time strings to datetime objects
        start_time = timezone.make_aware(datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M'))
        end_time = timezone.make_aware(datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M'))

        # Check if start time is before advisor's office hours start
        if start_time.time() < advisor.office_hours_start:
            error_message = "Advisor will be unavailable at the scheduled start time due to office hours."

        # Check if end time is after advisor's office hours end
        elif end_time.time() > advisor.office_hours_end:
            error_message = "Advisor will be unavailable at the scheduled end time due to office hours."

        else:
            # Create the appointment
            appointment = Appointment.objects.create(
                advisor=advisor,
                student=student,
                start_time=start_time,
                end_time=end_time,
                topic=topic,
                mode_of_meeting=mode_of_meeting,
                approved_by_student=True
            )

            # Create a notification for the advisor
            advisor_user = advisor.user
            message = f"An appointment has been scheduled by {student.user.get_full_name()}."
            Notification.objects.create(user=advisor_user, message=message)

            # Redirect to appointment detail page or any other page as needed
            return redirect('appointment_detail_student', appointment_id=appointment.id)

    return render(request, 'schedule_appointment_student.html', {'error_message': error_message})

def appointment_feedback(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Create a feedback instance
        feedback = Feedback.objects.create(appointment=appointment, rating=rating, comment=comment)
        feedback.save()

        advisor_user = appointment.advisor.user
        message = f"Feedback has been submitted for the appointment '{appointment.topic}'."
        Notification.objects.create(user=advisor_user, message=message)

        # Redirect to the appointment detail page after submitting feedback
        return redirect('appointment_detail_student', appointment_id=appointment_id)

    return render(request, 'appointment_feedback_student.html', {'appointment_id': appointment.id})

def appointment_history(request):
    appointments = Appointment.objects.filter(student=request.user.student, is_completed=True) | Appointment.objects.filter(student=request.user.student, is_rejected=True)
    appointments_without_feedback = [appointment for appointment in appointments if appointment.is_completed and not Feedback.objects.filter(appointment=appointment).exists()]

    return render(request, 'appointment_history_student.html', {'appointments': appointments})


def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.approved_by_student = True
    appointment.save()

    # Create notification for the student
    advisor_user = appointment.advisor.user
    message = "Appointment proposal has been agreed to by student. Check your appointments for more information."
    Notification.objects.create(user=advisor_user, message=message)

    return redirect('approved_appointments_student')

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
        appointment.approved_by_student = True
        appointment.approved_by_advisor = False
        appointment.save()

        # Create notification for the student
        advisor_user = appointment.advisor.user
        message = "I have proposed another appointment."
        Notification.objects.create(user=advisor_user, message=message)

        return redirect('view_appointments_student')
    else:
        return render(request, 'edit_appointment_student.html', {'appointment': appointment})


def view_tasks(request):
    # Fetch all uncompleted tasks related to the student
    uncompleted_tasks = Task.objects.filter(student=request.user.student,completed=False, failed=False)
    return render(request, 'view_tasks_student.html', {'tasks': uncompleted_tasks})

def mark_task_completed(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    # Mark the task as completed
    task.completed = True
    task.save()

    return redirect('view_tasks_student')


def student_notifications(request):
    # Retrieve notifications for the current student
    student_notifications = Notification.objects.filter(user=request.user)
    context = {
        'notifications': student_notifications
    }
    return render(request, 'notifications_student.html', context)

def task_history(request):
    tasks = Task.objects.filter(student=request.user.student, completed=True) | Task.objects.filter(student=request.user.student, failed=True)
    context = {'tasks': tasks}
    return render(request, 'task_history_student.html', context)

def view_appointments(request):
    appointments = Appointment.objects.filter(student=request.user.student,approved_by_student=False, is_completed=False, is_rejected=False)
    return render(request, 'view_appointments_student.html', {'appointments': appointments})

def logout_view(request):
    logout(request)
    return redirect('login_student')

def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Determine the status of the appointment
    if appointment.approved_by_advisor and appointment.approved_by_student:
        status = "Accepted"
    elif appointment.is_completed:
        status = "Completed"
    elif appointment.is_rejected:
        status = "Rejected"
    else:
        status = "Pending"
    
    return render(request, 'appointment_detail.html', {'appointment': appointment, 'status': status})
