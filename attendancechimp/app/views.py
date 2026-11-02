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
    from .models import InstructorProfile, StudentProfile
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
        from .models import StudentProfile
        StudentProfile.objects.create(user=user)
    else:
        from .models import InstructorProfile
        InstructorProfile.objects.create(user=user)

    login(request, user)
    return HttpResponse("User has been created successfully.")

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



