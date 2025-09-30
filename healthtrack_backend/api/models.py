from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    # Add related_name to resolve the clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='api_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='api_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    school_code = models.CharField(max_length=10)
    class_name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    roll_no = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    school_code = models.CharField(max_length=10)
    department = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='classrooms')
    class_name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    students = models.ManyToManyField(Student, related_name='classrooms')

    class Meta:
        unique_together = ('teacher', 'class_name', 'section')

    def __str__(self):
        return f"{self.class_name} - {self.section}"
class HealthData(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='health_records')
    date = models.DateField(auto_now_add=True)
    bpm = models.IntegerField()
    spo2 = models.IntegerField()
    breathe_rate = models.IntegerField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Health data for {self.student.name} on {self.date}"