"""
robot-models.py: LLM-generated data model for AttendanceChimp.

LLM: Claude 
Prompt: "Generate a Django models.py for an attendance tracking app called
AttendanceChimp. The app tracks class attendance via QR codes and it should have:
- InstructorProfile and StudentProfile (both extending Django's built-in User
  via OneToOneField)
- A Course table with name, instructor (FK to InstructorProfile), and meeting
  schedule (days and time)
- An Enrollment junction table linking students to courses (many-to-many)
- A Lecture table with course (FK), date (DateTimeField), and qr_code (CharField)
- A QRCodeUpload table with student (FK to StudentProfile), lecture (FK, nullable),
  image (FileField), and upload_time (DateTimeField)
Please include informative docstrings for each model."
"""
from django.db import models
from django.contrib.auth.models import User

class InstructorProfile(models.Model):
    """Instructor profile linked to Django User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Instructor: {self.user.get_full_name() or self.user.username}"

class StudentProfile(models.Model):
    """Student profile linked to Django User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, blank=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name() or self.user.username}"

class Course(models.Model):
    """A course taught by an instructor."""
    name = models.CharField(max_length=255)
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='courses')
    meeting_days = models.CharField(max_length=50, help_text="e.g. MWF or TTh")
    meeting_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.meeting_days} {self.meeting_time})"

class Enrollment(models.Model):
    """Many-to-many junction table between students and courses."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} in {self.course}"

class Lecture(models.Model):
    """A single class meeting with a unique QR code."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    date = models.DateTimeField()
    qr_code = models.CharField(max_length=255, unique=True)
    duration_minutes = models.IntegerField(default=60)

    def __str__(self):
        return f"{self.course} on {self.date.strftime('%Y-%m-%d')}"

class QRCodeUpload(models.Model):
    """A student's QR code upload for attendance."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='uploads')
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploads')
    image = models.FileField(upload_to='uploads/%Y/%m/%d/')
    upload_time = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f"Upload by {self.student} at {self.upload_time}"
