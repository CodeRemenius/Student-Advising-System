# Generated by Django 5.0.6 on 2024-05-26 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Advisor', '0005_student_advisor_student_department_student_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]