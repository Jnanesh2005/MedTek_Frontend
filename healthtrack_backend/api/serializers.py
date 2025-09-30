from rest_framework import serializers
from .models import Student, Teacher, HealthData, Classroom

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['name', 'school', 'class_name', 'section', 'roll_no']

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['name', 'school', 'school_code', 'department']

class HealthDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthData
        fields = ['bpm', 'spo2', 'breathe_rate', 'temperature']

class ClassroomSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Classroom
        fields = ['id', 'class_name', 'section', 'students']