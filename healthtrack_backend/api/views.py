from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, Student, Teacher, HealthData, Classroom
from .serializers import StudentSerializer, TeacherSerializer, HealthDataSerializer, ClassroomSerializer
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.db.models import Avg
from django.contrib.auth.hashers import make_password
import random
import string

class StudentRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name')
        school = request.data.get('school')
        class_name = request.data.get('class')
        section = request.data.get('section')
        roll_no = request.data.get('rollNo')
        
        if not all([name, school, class_name, section, roll_no]):
            return Response({"error": "Please fill in all fields"}, status=status.HTTP_400_BAD_REQUEST)

        school_code = ''.join([word[0] for word in school.split(' ')]).upper()
        student_id = f"{school_code}{roll_no.zfill(3)}"
        
        if User.objects.filter(username=student_id).exists():
            return Response({"error": "A student with this roll number is already registered in this school."}, status=status.HTTP_409_CONFLICT)
        
        temp_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        with transaction.atomic():
            user = User.objects.create(username=student_id, user_type="student", password=make_password(temp_password))
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                name=name,
                school=school,
                school_code=school_code,
                class_name=class_name,
                section=section,
                roll_no=roll_no
            )
        
        return Response({
            "message": "Registration successful!",
            "studentId": student_id,
            "password": temp_password
        }, status=status.HTTP_201_CREATED)

class TeacherRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        school = request.data.get('school')
        school_code = request.data.get('schoolCode')
        department = request.data.get('department')

        if not all([name, email, school, school_code]):
            return Response({"error": "Please fill in all required fields"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=email).exists():
            return Response({"error": "A teacher with this email is already registered."}, status=status.HTTP_409_CONFLICT)
        
        temp_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        user = User.objects.create_user(username=email, email=email, user_type="teacher", password=temp_password)
        teacher = Teacher.objects.create(
            user=user,
            name=name,
            school=school,
            school_code=school_code,
            department=department
        )

        return Response({"message": "Registration submitted for approval."}, status=status.HTTP_201_CREATED)

class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        student_id = request.data.get('studentId')
        password = request.data.get('password')

        user = authenticate(request, username=student_id, password=password)

        if user is not None:
            if user.user_type != "student":
                return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
            
            login(request, user)
            return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

class TeacherLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        school_code = request.data.get('schoolCode')
        
        try:
            user = User.objects.get(email=email)
            if user.user_type != "teacher":
                return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if user is not None and user.teacher.school_code == school_code:
            login(request, user)
            return Response({"message": "Verification successful."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials or school code."}, status=status.HTTP_400_BAD_REQUEST)

class HealthDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != "student":
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = HealthDataSerializer(data=request.data)
        if serializer.is_valid():
            student = get_object_or_404(Student, user=request.user)
            serializer.save(student=student)
            return Response({"message": "Vital signs recorded successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentHealthHistoryView(generics.ListAPIView):
    serializer_class = HealthDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != "student":
            return HealthData.objects.none()
        student = get_object_or_404(Student, user=self.request.user)
        return HealthData.objects.filter(student=student).order_by('-date')

class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != "teacher":
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        teacher = get_object_or_404(Teacher, user=request.user)
        
        class_name = request.query_params.get('class_name', '10th Grade')
        section = request.query_params.get('section', 'A')

        students = Student.objects.filter(
            school=teacher.school,
            class_name=class_name,
            section=section
        ).values('name', 'roll_no', 'health_records__date')

        avg_health_data = HealthData.objects.filter(
            student__school=teacher.school,
            student__class_name=class_name,
            student__section=section
        ).aggregate(
            avg_bpm=Avg('bpm'),
            avg_spo2=Avg('spo2'),
            avg_breathe_rate=Avg('breathe_rate'),
            avg_temperature=Avg('temperature')
        )
        
        return Response({
            "students": students,
            "analytics": avg_health_data
        })

    def post(self, request):
        return Response({"message": "Data entry successful."}, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)