"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""

from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                               # allows using logger.warning(), logger.error(), 
                                                               # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------
class InstructorProfile(models.Model):
    """Extends Django User for instructor specific data, one instructor profile per user account."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Instructor: {self.user.username}"

class StudentProfile(models.Model):
    """Extends Django User for student specific data, one student profile per user account."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Student: {self.user.username}"

# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------
class Course(models.Model):
    """Represents a course taught by one instructor that students can enroll in multiple courses."""
    name = models.CharField(max_length=255)
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    meeting_days = models.CharField(max_length=50)
    meeting_time = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------
class Enrollment(models.Model):
    """Links students and courses, allowing students to enroll in many courses and courses to have many students."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------
class Lecture(models.Model):
    """A single class meeting associated with a course. It has a unique QR code identifier for attendance tracking."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    qr_code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.course} - {self.date}"

# ---------------------------------------------------------------------------
# QR Code Upload
# ---------------------------------------------------------------------------
class QRCodeUpload(models.Model):
    """A student's uploaded QR code photograph, linked to a student and optionally to a lecture."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.FileField(upload_to='uploads/')
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload by {self.student} at {self.upload_time}"



# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------
def is_instructor(user):
    """Checks whether the user has an InstructorProfile."""
    return InstructorProfile.objects.filter(user=user).exists()

def is_student(user):
    """Checks whether the user has a StudentProfile."""
    return StudentProfile.objects.filter(user=user).exists()
