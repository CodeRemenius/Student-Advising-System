from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

DEPARTMENT_CHOICES = [
    ('Cybersecurity', 'Cybersecurity'),
    ('Software Engineering', 'Software Engineering'),
    ('Information Technology', 'Information Technology'),
    ('Computer Science', 'Computer Science'),
]
MEETING_CHOICES = [
    ('Online','Online'),
    ('Physical','Physical'),
]

class Advisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(default='201212076@nileuniversity.edu.ng')
    phone_number = models.CharField(max_length=15, default='08182006962')
    office_hours_start = models.TimeField(null=True)
    office_hours_end = models.TimeField(null=True)
    areas_of_expertise = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)

    def __str__(self):
        return self.user.get_full_name()  # Assuming the User model has first_name and last_name fields

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(default='201212076@nileuniversity.edu.ng')
    phone_number = models.CharField(max_length=15, default='08182006962')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='')

    def __str__(self):
        return self.user.get_full_name()

class Appointment(models.Model):
    advisor = models.ForeignKey(Advisor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    topic = models.CharField(max_length=255)
    mode_of_meeting = models.CharField(max_length=50, choices=MEETING_CHOICES, default='')
    approved_by_advisor = models.BooleanField(default=False)
    approved_by_student = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

class Feedback(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Can be a rating scale from 1 to 5
    comment = models.TextField()

class AdvisingHours(models.Model):
    advisor = models.ForeignKey(Advisor, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)  # Monday, Tuesday, etc.
    start_time = models.TimeField()
    end_time = models.TimeField()

class Task(models.Model):
    advisor = models.ForeignKey('Advisor', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    completed = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Update the failed status based on the deadline
        if not self.completed and not self.failed:
            now = timezone.now()
            if now > self.deadline:
                self.failed = True
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
