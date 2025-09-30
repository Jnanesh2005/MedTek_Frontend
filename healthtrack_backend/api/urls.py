from django.urls import path
from .views import (
    StudentRegistrationView,
    TeacherRegistrationView,
    StudentLoginView,
    TeacherLoginView,
    HealthDataView,
    StudentHealthHistoryView,
    TeacherDashboardView,
)

urlpatterns = [
    path('register/student/', StudentRegistrationView.as_view(), name='student-register'),
    path('register/teacher/', TeacherRegistrationView.as_view(), name='teacher-register'),
    path('login/student/', StudentLoginView.as_view(), name='student-login'),
    path('login/teacher/', TeacherLoginView.as_view(), name='teacher-login'),
    path('student/health-data/', HealthDataView.as_view(), name='student-health-data'),
    path('student/health-history/', StudentHealthHistoryView.as_view(), name='student-health-history'),
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
]