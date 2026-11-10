"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io

#from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)
try:
    from .models import (InstructorProfile, StudentProfile, Course, Lecture, QRCodeUpload)
except ImportError:
    pass
CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    """Render the home page (index.html)."""

    now = datetime.now(tz=CDT)
    context = {
	'current_time': now.strftime("%H:%M")
    }
    return render(request, 'app/index.html', context)

def time_view(request):
    now = datetime.now(tz=CDT)
    return HttpResponse(now.strftime("%H:%M"))

def sum_view(request):
    n1 = float(request.GET.get('n1', 0))
    n2 = float(request.GET.get('n2', 0))
    result = n1 + n2
    return HttpResponse(f"<p>{result}</p>")


# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------
def new_user(request):
    """Display the sign up forms, only accepts GET requests."""
    if request.method =='POST':
        return HttpResponseBadRequest("POST is not allowed on this endpoint.")
    return render(request, 'app/new.html', {})

@csrf_exempt
def createUser(request):
    """Creates a new User, only accepts POST requests."""
    if request.method == 'GET':
        return HttpResponseBadRequest("GET not allowed on this endpoint.")

    email = request.POST.get('email')
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    is_student = request.POST.get('is_student')

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest("A user with this email already exists.")
    if User.objects.filter(username=user_name).exists():
        return HttpResponseBadRequest("A user with this username already exists.")

    user = User.objects.create_user(username=user_name, email=email, password=password)

    if is_student == '1':
        try:
            from .models import StudentProfile
            StudentProfile.objects.create(user=user)
        except ImportError:
            pass
    else:
        try:
            from .models import InstructorProfile
            InstructorProfile.objects.create(user=user)
        except ImportError:
            pass

    login(request, user)
    return HttpResponse("User has been created successfully.")

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------
def new_course(request):
    """Display the create course form, only accepts GET requests."""
    if request.method =='POST':
        return HttpResponseBadRequest("POST is not allowed on this endpoint.")
    return render(request, 'app/new_course.html', {})
def new_lecture(request):
    """Display the create lecture form, only accepts GET requests."""
    if request.method =='POST':
        return HttpResponseBadRequest("POST is not allowed on this endpoint.")
    return render(request, 'app/new_lecture.html', {})
def new_qr_upload(request):
    """Display the QR code upload form, only accepts GET requests."""
    if request.method =='POST':
        return HttpResponseBadRequest("POST is not allowed on this endpoint.")
    return render(request, 'app/new_qr_upload.html', {})
@csrf_exempt
def createCourse(request):
   """Creates new course, only accepts POST requests. Instructor only."""
   if request.method !='POST':
      return HttpResponseBadRequest("Only POST requests are allowed.")

   if not request.user.is_authenticated:
      return HttpResponse("Not logged in.", status=401)

   try:
      instructor = InstructorProfile.objects.get(user=request.user)
   except:
      return HttpResponse("Only instructors can create courses.", status=401)

   course_name = request.POST.get('course-name')
   meeting_days = []
   for day in ['mon', 'tue', 'wed','thu','fri']:
      if request.POST.get(f'day-{day}'):
         meeting_days.append(day)
   meeting_days = ','.join(meeting_days)
   start_time = request.POST.get('start-time')
   end_time = request.POST.get('end-time')
   meeting_time = f"{start_time}-{end_time}"

   Course.objects.create(
       name=course_name,
       instructor=instructor,
       meeting_days=meeting_days,
       meeting_time=meeting_time
   )
   return HttpResponse("Course created successfully.")
@csrf_exempt
def createLecture(request):
   """Creates new lecture, only accepts POST requests. Instructor only."""
   if request.method !='POST':
      return HttpResponseBadRequest("Only POST requests are allowed.")

   if not request.user.is_authenticated:
      return HttpResponse("Not logged in.", status=401)
    
   try:  
      instructor = InstructorProfile.objects.get(user=request.user)
   except:
      return HttpResponse("Only instructors can create lectures.", status=401)
        
   course_name = request.POST.get('choice')
   
   try:
      course = Course.objects.get(name=course_name)
   except Course.DoesNotExist:
      return HttpResponseBadRequest("Course not found.")
    
   import random
   import string
   qr_code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
   date = request.POST.get('date')
    
   Lecture.objects.create(
       course=course,
       date=date,
       qr_code=qr_code
   )
   return HttpResponse("Lecture created successfully.")
@csrf_exempt
def createQRCodeUpload(request):
   """Creates a new QR code upload, only accepts POST requests. Student only."""
   if request.method !='POST':
      return HttpResponseBadRequest("Only POST requests are allowed.")
   
   if not request.user.is_authenticated:
      return HttpResponse("Not logged in.", status=401)
       
   try:
      student = StudentProfile.objects.get(user=request.user)
   except:
      return HttpResponse("Only students can upload QR codes.", status=401)

   image = request.FILES.get('imageUpload')
   lecture_id = request.POST.get('lecture_id')
   
   lecture = None
   if lecture_id:
      try:
         lecture = Lecture.objects.get(id=lecture_id)
      except Lecture.DoesNotExist:
         pass
   
   QRCodeUpload.objects.create(
      student=student,
      lecture=lecture,
      image=image
   )
   return HttpResponse("QR code uploaded successfully.") 
def dumpUploads(request):
   """Returns a JSON list of all QR code uploads, instructor only"""
   if not request.user.is_authenticated:
      return HttpResponse("Not logged in.", status=401)
   try:
      InstructorProfile.objects.get(user=request.user)
   except:
      return HttpResponse("Only instructors can view uploads.", status=401)

   uploads = QRCodeUpload.objects.all()
   data = [
      {
         "username": upload.student.user.username,
         "upload_time": str(upload.upload_time)
      }
      for upload in uploads
   ]
   return JsonResponse(data, safe=False)
# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



