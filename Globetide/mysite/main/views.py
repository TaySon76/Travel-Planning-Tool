from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date, datetime
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import UserProfileSerializer
from .models import UserProfile, AdditionalData, Trip, Budget, City, BudgetItem, SharedTrip, UserActivity, archivedTrips, Notification, BlogComment, BlogPost, UserBlogLikes
from rest_framework_simplejwt.tokens import RefreshToken
from .generate_random_digits import generate_random_digits, generate_random_digits_large
from .notification_notify import new_notification
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpRequest
from django.urls import reverse
from django.views import View
import json
import jwt 
from .secrets import secret_key
import base64
from .secrets import secret_key
from django.http import JsonResponse
from django.utils.html import escape
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.contrib import messages
import requests
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from calendar import monthrange
from geopy.geocoders import Nominatim
import pytz 
from timezonefinder import TimezoneFinder
import folium
from deep_translator import GoogleTranslator
import sys, os
from langdetect import detect
from cryptography.fernet import Fernet
from django import forms
import mimetypes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from amadeus import Client, ResponseError, Location
import time
from .KeyRotation import keys
import simplejson
from operator import itemgetter
from django.db.models import Q


SECRET_KEY = os.urandom(32)
BLOCK_SIZE = 16
sys.stdout.reconfigure(encoding='utf-8')

amadeus = Client(client_id='u6bpzmGFnxEJ18MR6wRi69cj8aPEZ6OG', client_secret='qXqQGbWkNvB4me6H')


def select_destination(req, param):
    if req.method == "GET":
        start_time = time.time()  # Record the start time
        context = {"data": []}
        try:
            print(param)
            for i in range(2):
                try:
                    response = amadeus.reference_data.locations.get(
                        keyword=param, subType=Location.ANY)
                    context["data"].append(response.data)
                except ResponseError as error:
                    print(f"Hello, error at iteration {i}")
                    print(error)
                    break
                time.sleep(1)  # Adjust sleep time as needed
        except Exception as error:
            print("Unexpected error:", error)
            return JsonResponse({"error": "An unexpected error occurred"})
        finally:
            end_time = time.time()  # Record the end time
            total_runtime = end_time - start_time
            print(f"Total runtime: {total_runtime} seconds")

        return JsonResponse(context)

    return render(req, 'main/key.html')


class UploadFileForm(forms.Form):
    file = forms.FileField()

def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        recaptcha_verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        response = requests.post(recaptcha_verify_url, data=data)
        result = response.json()

        if result['success']:
            if pass1 == pass2:
                user = User.objects.create_user(username, email, pass1)
                user.save()

                Notification.objects.create(
                        user=user,
                        title="Welcome to Globetide!",
                        description="Continue filling out your profile",
                        date=date.today(),
                        link='/profile',
                    )

                try:
                    additional_data = AdditionalData.objects.get(user_profile__user=user)
                except AdditionalData.DoesNotExist:
                    additional_data = AdditionalData.objects.create(user_profile=UserProfile.objects.get(user=user))

                additional_data.firstname = request.POST.get('FirstName')
                additional_data.lastname = request.POST.get('LastName')
                date_str = f"{request.POST.get('dob-year')}-{request.POST.get('dob-month')}-{request.POST.get('dob-day')}"
                try:
                    additional_data.dateofbirth = date_str
                except ValueError:
                    return HttpResponse('Invalid date format')
                additional_data.phone_no = request.POST.get('PhoneNumber')
                additional_data.country_origin = request.POST.get('Country')
                additional_data.city_origin = request.POST.get('City')
                additional_data.save()
                
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match")
        else:
            messages.error(request, "Invalid reCAPTCHA. Please try again.")
    return render(request, 'main/signup.html')

@csrf_exempt
def login1(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password1') 
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                additional_data = AdditionalData.objects.get(user_profile__user=user)
            except AdditionalData.DoesNotExist:
                return redirect('firstlogin')
            
            print("yee")
            user_profile = UserProfile.objects.get(user=user)
            print(user_profile)
            verification_code = generate_random_digits()
            user_profile.otp = verification_code
            user_profile.otp_expiry_time = timezone.now() + timedelta(minutes=15)
            user_profile.save()
            send_mail(
                'Verification Code',
                f'Your verification code is: {verification_code}',
                'rt.scheduling.automailer@gmail.com',
                [user.email],
                fail_silently=False,
            )

            request.session['username'] = username
            request.session['password'] = password
            request.session.save()

            return redirect('otp')
        else:
            error_message = "Invalid username or password"
            return render(request, 'main/login.html', {'error_message': error_message})
    return render(request, 'main/login.html')

@csrf_exempt
def verify(request):
    username = request.session['username']
    password = request.session['password']
    try:
        username = request.session['username']
        password = request.session['password']
    except(KeyError or UnboundLocalError):
        login(request, authenticate(request, username=username, password=password))
        
    user = authenticate(request, username=username, password=password)
    user_profile = UserProfile.objects.get(user=user)
    print(f'The actual code {user_profile.otp}')
    wrong_otp = False  
    otp_empty = False  
    if request.method == 'POST':
        otp = request.POST.get('otp', '')
        print("Received OTP:", otp)
        if (
            user_profile.otp == otp and
            user_profile.otp_expiry_time is not None and
            user_profile.otp_expiry_time > timezone.now()
        ):
            user_activity, created = UserActivity.objects.get_or_create(user=user)
            today = timezone.now().date().isoformat()
            user_activity.login_dates[today] = user_activity.login_dates.get(today, 0) + 1
            user_activity.save()
            login(request, user) 
            archived_trips, created = archivedTrips.objects.get_or_create(user=user)
            user_trips = Trip.objects.filter(user=request.user, is_shared=False)
            shared_trips_items = SharedTrip.objects.filter(email=request.user.email)

            for trip in user_trips:
                if trip.end_date < date.today():
                    archived_trips.trips.append({
                        'id': trip.trip_id,
                        'destination': trip.destination,
                        'start_date': str(trip.start_date),
                        'end_date': str(trip.end_date),
                        'is_shared': trip.is_shared
                    })

            for shared_trip_item in shared_trips_items:
                if shared_trip_item.trip.end_date < date.today():
                    archived_trips.trips.append({
                        'id': shared_trip_item.trip.trip_id,
                        'destination': shared_trip_item.trip.destination,
                        'start_date': str(shared_trip_item.trip.start_date),
                        'end_date': str(shared_trip_item.trip.end_date),
                        'is_shared': shared_trip_item.trip.is_shared
                    })

            archived_trips.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_profile.otp = ''
            user_profile.otp_expiry_time = None
            user_profile.save()

            return redirect('home')
        else:
            wrong_otp = True
        if not otp:
            otp_empty = True

    return render(request, 'main/otp.html', {'wrong_otp': wrong_otp, 'otp_empty': otp_empty, 'otp': user_profile.otp})

#@login_required
def home(response):
    context = {
        'notify': new_notification(response.user),
    }
    return render(response, 'main/landing_page.html', context)

def test(response):
    return render(response, 'main/test.html')

@login_required
@csrf_exempt
def profile(request):
    try:
        additional_data = AdditionalData.objects.get(user_profile__user=request.user)
        login_dates = UserActivity.objects.get(user=request.user).login_dates
        login_dataj= json.dumps(login_dates)

        today = date.today()
        year = today.year
        month = today.month

        sign_ins = []
        for i in range(1, monthrange(year, month)[1]+1):
            sign_ins.append(login_dates.get(f"{year}-{month:02}-{i:02}", 0))

        if request.method == 'POST':
            new_username = request.POST.get('username', None)
            if new_username != request.user.username:
                if User.objects.filter(username=new_username).exists():
                    return HttpResponse('Username already exists')
                else:
                    request.user.username = new_username
                    request.user.save()
                    update_session_auth_hash(request, request.user)
            
            additional_data.firstname = request.POST.get('first-name')
            additional_data.lastname = request.POST.get('last-name')
            additional_data.address = request.POST.get('address')
            additional_data.city_origin = request.POST.get('city')
            additional_data.country_origin = request.POST.get('country')
            additional_data.sex = request.POST.get('sex')
            additional_data.dateofbirth = request.POST.get('dob')
            additional_data.phone_no = request.POST.get('phone')
            additional_data.save()
            
        context = {
            'additional_data': additional_data,
            'login_data': login_dataj,
            'login_data': login_dataj,
            'sign_ins': sign_ins,
            'notify': new_notification(request.user),
        }
        return render(request, 'main/profile.html', context)
    except AdditionalData.DoesNotExist:
        return HttpResponse('Additional data not found')

@login_required
def budget(request, jwt_token = None):
    try:
        try:
            my_user = request.user
            email = my_user.email

            trip_id = request.GET.get('trip_id')
            trip = Trip.objects.filter(trip_id=trip_id).first()
            trip1 = Trip.objects.filter(jwt_token=jwt_token).first()
            if trip1 == trip and my_user == User.objects.filter(email=email).first():
                check_trip = bool(SharedTrip.objects.filter(email=email).filter(trip=trip).first())
                user = trip.user
            elif not User.objects.filter(email=email).first():
                return redirect('/')
            elif trip != trip1:
                raise LookupError

        except:
            user = request.user
            trip_id = request.GET.get('trip_id')
            trip = Trip.objects.filter(user=user).filter(trip_id=trip_id).first()
            check_trip = bool(trip)
        
        if check_trip:
            budget = Budget.objects.filter(user=user).get(trip=trip)

            total_budget = budget.total_amount
            budget_objects = BudgetItem.objects.filter(budget=budget)
            budget_items = []

            for obj in budget_objects:
                budget_items.append(obj.make_list())

            if request.method == 'POST':
                budget_objects.delete()

                data = json.loads(request.body)
                total_budget = data.get('totalBudget')
                expenses = data.get('expenses')

                budget.total_amount = total_budget
                budget.save()

                for expense in expenses:
                    try:
                        BudgetItem.objects.create(
                            budget = budget,
                            description = expense[0],
                            type = expense[1],
                            date = expense[2],
                            quantity = expense[3],
                            unit_cost = expense[4]
                        )
                    except:
                        pass
            
            context = {
                'trip_id': trip_id,
                'total_budget': total_budget,
                'budget_items': budget_items,
                'test': test,
                'jwt_token': jwt_token,
                'notify': new_notification(request.user),
            }

            return render(request, 'main/budget.html', context)
    except Trip.DoesNotExist:
        return redirect('create-trip')
    except:
        print("Something brokie")
        return redirect('/home')
    
def create_trip(request):
    if request.method == "POST":
        destination = request.POST.get("destination")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        trip_id = generate_random_digits_large()

        trip = Trip.objects.create(
            user=request.user,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            trip_id=trip_id
        )

        trip.save()
        
        Budget.objects.create(
            budget_id = generate_random_digits_large(),
            user = request.user,
            trip = trip,
            total_amount = 10_000,
            currency = 'USD'
        )

        return redirect(f'/email/{trip_id}')

    context = {
        'notify': new_notification(request.user),
    }

    return render(request, 'main/tripcreation.html', context)

def email(request, trip_id):
    try:
        user = request.user
        trip = Trip.objects.filter(user=user).get(trip_id=trip_id)

        if request.method == 'POST':
            data = json.loads(request.body)
            print(data)
            shareable = f"http://localhost:8000/budget/{trip.jwt_token}/?trip_id={trip_id}"
            noti_share_link = f"/budget/{trip.jwt_token}/?trip_id={trip_id}"
            for email in data:
                send_mail(
                        'Shareable link:',
                        f'{shareable}',
                        'rt.scheduling.automailer@gmail.com',
                        [email],
                        fail_silently=False,
                    ) 
                
                try:
                    share_user = User.objects.get(email=email)
                    Notification.objects.create(
                        user=share_user,
                        title="Someone added you to their trip!",
                        description="Go to shared trip",
                        date=date.today(),
                        link=noti_share_link,
                    )
                except:
                    pass
                
                SharedTrip.objects.create(
                    trip=trip,
                    email=email,
                )
                
            redirect_url = reverse('budget') + f'?trip_id={trip_id}'
            return JsonResponse({'redirect_url': redirect_url})
    except:
        pass

    context = {
        'notify': new_notification(request.user),
        'trip_id': trip_id,
    }

    return render(request, 'main/addemailsshare.html', context)

@csrf_exempt
def reset_check_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"http://localhost:8000/reset_user_password/{uid}/{token}/"
            s = f'Please follow this link to reset your password: {reset_link}'
            send_mail(
                    'Change Password for Globetide',
                    f'{s}',
                    'rt.scheduling.automailer@gmail.com',
                    [email],
                    fail_silently=False,
                )
            return JsonResponse({'exists': True})
        else:
            return JsonResponse({'exists': False})
            
    return render(request, 'main/password_reset.html')
    
def reset_user_password(request, uid, token):
    if request.method == 'POST':
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
        password = request.POST.get('password')
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(password)
            print(user.password)
            user.save()
            return redirect('login')

    return render(request, 'main/password_reset_form.html')

def test(request):
    if request.user.is_authenticated:
        archived_trips = archivedTrips.objects.get(user=request.user).trips
        user_trips = Trip.objects.filter(user=request.user, is_shared=False)
        shared_trips_items = SharedTrip.objects.filter(email=request.user.email)
        ut_final, shared_trips = [], []
        ut_len, st_len = len(user_trips), len(shared_trips_items)
        
        if ut_len > st_len:
            for i in range(ut_len):
                if i < st_len:
                    st_check = {'id': shared_trips_items[i].trip.trip_id, 'destination': shared_trips_items[i].trip.destination, 'start_date': str(shared_trips_items[i].trip.start_date), 'end_date': str(shared_trips_items[i].trip.end_date), 'is_shared': shared_trips_items[i].trip.is_shared}
                    if st_check not in archived_trips and st_check is not None:
                        shared_trips.append(st_check)
                t_check =  {'id': user_trips[i].trip_id, 'destination': user_trips[i].destination, 'start_date': str(user_trips[i].start_date), 'end_date': str(user_trips[i].end_date), 'is_shared': user_trips[i].is_shared}
                if t_check not in archived_trips:
                    ut_final.append(t_check)

                    
        elif st_len > ut_len:
            for i in range(st_len):
                if i < ut_len:
                    t_check = {'id': user_trips[i].trip_id, 'destination': user_trips[i].destination, 'start_date': str(user_trips[i].start_date), 'end_date': str(user_trips[i].end_date), 'is_shared': user_trips[i].is_shared}
                    if t_check not in archived_trips and t_check is not None:
                        ut_final.append(t_check)
                st_check = {'id': shared_trips_items[i].trip.trip_id, 'destination': shared_trips_items[i].trip.destination, 'start_date': str(shared_trips_items[i].trip.start_date), 'end_date': str(shared_trips_items[i].trip.end_date), 'is_shared': shared_trips_items[i].trip.is_shared}
                if st_check not in archived_trips:
                    shared_trips.append(st_check)
        
        context = {
            'user_trips': ut_final,
            'shared_trips': shared_trips,
            'archived_trips': archived_trips
        }
    
        shared_trips = []
        ut_final = []
        
        return render(request, 'main/test.html', context)

def dashboard(request):
    if request.user.is_authenticated:
        archived_trips = archivedTrips.objects.get(user=request.user).trips
        user_trips = Trip.objects.filter(user=request.user, is_shared=False)
        shared_trips_items = SharedTrip.objects.filter(email=request.user.email)
        ut_final, shared_trips = [], []
        ut_len, st_len = len(user_trips), len(shared_trips_items)
        
        if ut_len > st_len:
            for i in range(ut_len):
                if i < st_len:
                    st_check = {'id': shared_trips_items[i].trip.trip_id, 'destination': shared_trips_items[i].trip.destination, 'start_date': str(shared_trips_items[i].trip.start_date), 'end_date': str(shared_trips_items[i].trip.end_date), 'is_shared': shared_trips_items[i].trip.is_shared}
                    if st_check not in archived_trips and st_check is not None:
                        shared_trips.append(st_check)
                t_check =  {'id': user_trips[i].trip_id, 'destination': user_trips[i].destination, 'start_date': str(user_trips[i].start_date), 'end_date': str(user_trips[i].end_date), 'is_shared': user_trips[i].is_shared}
                if t_check not in archived_trips:
                    ut_final.append(t_check)

                    
        elif st_len > ut_len:
            for i in range(st_len):
                if i < ut_len:
                    t_check = {'id': user_trips[i].trip_id, 'destination': user_trips[i].destination, 'start_date': str(user_trips[i].start_date), 'end_date': str(user_trips[i].end_date), 'is_shared': user_trips[i].is_shared}
                    if t_check not in archived_trips and t_check is not None:
                        ut_final.append(t_check)
                st_check = {'id': shared_trips_items[i].trip.trip_id, 'destination': shared_trips_items[i].trip.destination, 'start_date': str(shared_trips_items[i].trip.start_date), 'end_date': str(shared_trips_items[i].trip.end_date), 'is_shared': shared_trips_items[i].trip.is_shared}
                if st_check not in archived_trips:
                    shared_trips.append(st_check)
        
        context = {
            'user_trips': ut_final,
            'shared_trips': shared_trips,
            'archived_trips': archived_trips,
            'notify': new_notification(request.user),
        }
    
        shared_trips = []
        ut_final = []
        
        return render(request, 'main/dashboard.html', context)

def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    trip.delete()
    return JsonResponse({'message': 'Trip deleted successfully'})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_shared_trip(request, trip_id):
    try:
        shared_trip = get_object_or_404(SharedTrip, trip_id=trip_id, email=request.user.email)
        shared_trip.delete()
        return JsonResponse({'message': 'Trip left successfully'}, status=200)
    except SharedTrip.DoesNotExist:
        return JsonResponse({'error': 'SharedTrip not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def logindata(request):
    login_dates = UserActivity.objects.get(user=request.user).login_dates
    login_dataj= json.dumps(login_dates)

    today = date.today()
    year = today.year
    month = today.month

    sign_ins = []
    for i in range(1, monthrange(year, month)[1]+1):
        sign_ins.append(login_dates.get(f"{year}-{month:02}-{i:02}", 0))

    context = {
    'login_data': login_dataj,
    'sign_ins': sign_ins,
    }
    return render(request, 'main/logindata.html', context)

def revised(request):
    return render(request, 'main/reviseddash.html')

def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my_custom_app")
    location = geolocator.reverse((latitude, longitude))
    if location is None:
        return None

    address = location.raw['address']
    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')

    if state:
        location_name = f"{city}, {state}, {country}"
    else:
        location_name = f"{city}, {country}"
    
    return location_name.strip(", ")

def get_utc_offset(lat, lng):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lng, lat=lat)
    
    if timezone_str is None:
        return None  
    
    local_time = datetime.now(pytz.timezone(timezone_str))
    utc_offset = local_time.utcoffset()
    
    return utc_offset

def weather(request, latitude, longitude):
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}"
    count = 0
    headers = {
        "User-Agent": "MyCustomUserAgent/1.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        timeseries = data["properties"]["timeseries"]
        weather_dict = {}
        location_name = get_location_name(latitude, longitude)
        
        utc_offset = get_utc_offset(latitude, longitude)
        for data_point in timeseries:   
            time_utc = data_point["time"]
            time_utc_parsed = datetime.fromisoformat(time_utc[:-1])
            
            while count < 1:
                if "day" in str(utc_offset):
                    days, time_str = str(utc_offset).split(", ")
                    hours, minutes, seconds = map(int, time_str.split(":"))
                    adjustment = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    adjusted_time = time_utc_parsed - (timedelta(days=1) - adjustment)
                    time_utc_parsed = adjusted_time
                
                else:
                    hours, minutes, seconds = map(int, str(utc_offset).split(":"))
                    adjustment = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    adjusted_time = time_utc_parsed + adjustment
                    time_utc_parsed = adjusted_time
                count += 1
            date_local_str = time_utc_parsed.strftime('%Y-%m-%d')

            if date_local_str == datetime.now().strftime('%Y-%m-%d'):
                time_local_str = adjusted_time.strftime('%A, %B %d, %Y at %I:%M %p').replace(" 0", " ")
                air_temp = data_point["data"]["instant"]["details"]["air_temperature"]
                humidity = data_point["data"]["instant"]["details"]["relative_humidity"]
                wind_speed = data_point["data"]["instant"]["details"]["wind_speed"]
                air_pressure = data_point["data"]["instant"]["details"]["air_pressure_at_sea_level"]
                summary = data_point["data"].get("next_1_hours", {}).get("summary", {}).get("symbol_code", None)
                precip_next_hour_details = data_point["data"].get("next_1_hours", {}).get("details", {})
                precip_next_hour = precip_next_hour_details.get("precipitation_amount", None)
                
                if date_local_str not in weather_dict:
                    weather_dict[date_local_str] = {
                        "time": time_local_str,
                        "temperature": air_temp,
                        "humidity": humidity,
                        "wind_speed": wind_speed,
                        "air_pressure": air_pressure,
                        "summary": summary,
                        "precip_next_hour": precip_next_hour,
                        "location_name": location_name,
                        "max_temp": float('-inf'),
                        "min_temp": float('inf')
                    }

                if air_temp > weather_dict[date_local_str]["max_temp"]:
                    weather_dict[date_local_str]["max_temp"] = air_temp
                if air_temp < weather_dict[date_local_str]["min_temp"]:
                    weather_dict[date_local_str]["min_temp"] = air_temp

        context = {
            'weather_dict1': simplejson.dumps(weather_dict),
            'weather_dict': weather_dict,
            'notify': new_notification(request.user),
        }
        
    return render(request, 'main/weather.html', context)


def back(request):
    return render(request, 'main/back.html')

def notifications(request):
    user = request.user

    notifications = Notification.objects.filter(user=user)
    notifications.update(unread=False)

    for n in notifications:
        n.save()

    recent = []
    earlier = []

    for n in notifications:
        if (date.today() - n.date).days <= 3:
            recent.append(n)
        else:
            earlier.append(n)

    recent = sorted(recent, key=lambda x: x.date, reverse=True)
    earlier = sorted(earlier, key=lambda x: x.date, reverse=True)

    context = {
        "recent": recent,
        "earlier": earlier,
        'notify': new_notification(request.user),
    }

    return render(request, 'main/notifications.html', context)

def password_reset_sent(request):
    return render(request, 'main/password_reset_sent.html')

def blog_general(request):
    return render(request, 'main/blog_general.html')

def map_view(request, latitude, longitude):

    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    folium.Marker(
        location=[latitude, longitude],
        popup='Portland, OR',
        icon=folium.Icon()
    ).add_to(m)

   
    map_html = m._repr_html_()

    return render(request, 'main/map.html', {'map_html': map_html, 'lat':latitude, 'long':longitude})

def blog(request, category, username=None, id=None):
    print(BlogPost.objects.filter().first().id)
    if username == None and id == None:
        if category == 'all':
            blogs = BlogPost.objects.filter()

            context = {
                'category': category,
                'blogs': blogs,
            }
        
        elif category == 'travel':
            blogs = BlogPost.objects.filter(category='travel')

            context = {
                'category': category,
                'blogs': blogs,
            }
        
        elif category == 'eat':
            blogs = BlogPost.objects.filter(category='eat')

            context = {
                'category': category,
                'blogs': blogs,
            }
        
        elif category == 'relax':
            blogs = BlogPost.objects.filter(category='relax')

            context = {
                'category': category,
                'blogs': blogs,
            }
        
        return render(request, 'main/blog_home.html', context)
        
    elif not BlogPost.objects.filter(user=User.objects.filter(username=username).first(), id=id): # if the user does not have a blog with that id (no logic for this yet)
        return redirect('/blog/all')

    else:
        blog = BlogPost.objects.get(user=User.objects.filter(username=username).first(), id=id)

        if request.method == "POST":
            data = json.loads(request.body)
            print(data)
            '''comment = BlogComment.objects.create(
                user=request.user,
                blog=blog,
                comment=data["comment"],
                likes=0,
            )

            comment.save()'''
        
        comments = reversed(BlogComment.objects.filter(blog=blog))

        context = {
            'blog': blog,
            'comments': comments,
            'username': request.user.username,
        }

        return render(request, 'main/blog_post.html', context)

def create_blog(request):
    context = {
    }
    return render(request, 'main/create_blog.html', context)

def translate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data['text']
        first, target_language = data['first_language'], data['target_language']
        compliments = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'assamese': 'as', 'aymara': 'ay', 'azerbaijani': 'az', 'bambara': 'bm', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bhojpuri': 'bho', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dhivehi': 'dv', 'dogri': 'doi', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'ewe': 'ee', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'guarani': 'gn', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'ilocano': 'ilo', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 'konkani': 'gom', 'korean': 'ko', 'krio': 'kri', 'kurdish (kurmanji)': 'ku', 'kurdish (sorani)': 'ckb', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lingala': 'ln', 'lithuanian': 'lt', 'luganda': 'lg', 'luxembourgish': 'lb', 'macedonian': 'mk', 'maithili': 'mai', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'meiteilon (manipuri)': 'mni-Mtei', 'mizo': 'lus', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia (oriya)': 'or', 'oromo': 'om', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'quechua': 'qu', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'sanskrit': 'sa', 'scots gaelic': 'gd', 'sepedi': 'nso', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'tatar': 'tt', 'telugu': 'te', 'thai': 'th', 'tigrinya': 'ti', 'tsonga': 'ts', 'turkish': 'tr', 'turkmen': 'tk', 'twi': 'ak', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}
        if first.lower() == "detect language":
            first = detect(text)
            translation = GoogleTranslator(source=first, target=compliments[target_language.lower()]).translate(text)
     
            result = [l for l, f in compliments.items() if f == f"{first}"]    
            first = result[0].capitalize()
            return JsonResponse({'translation': translation, 'first':first})
        else:
            translation = GoogleTranslator(source=compliments[first.lower()], target=compliments[target_language.lower()]).translate(text)
            return JsonResponse({'translation': translation, 'first':first})

    return render(request, 'main/translate.html')

'''
class TranslateView(View):
    def post(self, request, *args, **kwargs):
        text = request.POST.get('text')
        target_language = request.POST.get('target_language')
        print(text, target_language)

        # Translate text to the target language using your preferred translation method
        translation = GoogleTranslator(source='en', target=f'ur').translate(text)

        # Return JSON response
        return JsonResponse({'translation': translation})

    def get(self, request, *args, **kwargs):
        # Handle GET requests (render the translation form)
        return render(request, 'main/translate.html')
'''

def mapo(request):
    return render(request, 'main/testmap.html')

def pad(s):
    padding = BLOCK_SIZE - len(s) % BLOCK_SIZE
    return s + chr(padding) * padding

def unpad(s):
    padding = s[-1]
    return s[:-padding]

def encrypt(raw):

    key = SECRET_KEY.encode('utf-8')

    iv = os.urandom(BLOCK_SIZE)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(pad(raw).encode('utf-8')) + encryptor.finalize()

    combined = iv + ciphertext
    encrypted_data = base64.b64encode(combined).decode('utf-8')

    return encrypted_data

def decrypt(enc):
    key = SECRET_KEY.encode('utf-8')

    enc = base64.b64decode(enc)

    iv = enc[:BLOCK_SIZE]
    ciphertext = enc[BLOCK_SIZE:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    return unpad(decrypted_data.decode('utf-8'))

@login_required
def upload_sd(request):
    if request.method == 'POST':
        image_data = request.POST.get('image_data')
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)

        encrypted_data = encrypt(image_data)
        decrypted_data = decrypt(encrypted_data)

        return JsonResponse({'encrypted_data': encrypted_data, 'decrypted_data': decrypted_data})

    return render(request, 'main/upload_sd.html')

def cow(request):
    return render(request, 'main/searchbar.html')

@login_required
def trip_overview(request):
    if request.user.is_authenticated:
        archived_trips = archivedTrips.objects.get(user=request.user).trips
        user_trips = Trip.objects.filter(user=request.user, is_shared=False)
        print(user_trips)
        shared_trips_items = SharedTrip.objects.filter(email=request.user.email)
        '''
        trip0 = Trip.objects.get(pk=263197458).end_date
        trip1 = Trip.objects.get(pk=4826539071).end_date
        trip2 = Trip.objects.get(pk=7314290586).end_date
        '''
        ut_final, shared_trips = [], []
        ut_len, st_len = len(user_trips), len(shared_trips_items)
        total = UserProfile.objects.get(user=request.user).total       
        tot = []
        trt = []
        brt = []
        if not total:
            print('theres no total')
            if ut_len > st_len:
                for i in range(ut_len):
                    if i < st_len:
                        st_check = {'id': shared_trips_items[i].trip.trip_id, 'destination': shared_trips_items[i].trip.destination, 'start_date': str(shared_trips_items[i].trip.start_date), 'end_date': str(shared_trips_items[i].trip.end_date), 'is_shared': shared_trips_items[i].trip.is_shared}
                        if st_check not in archived_trips and st_check is not None:
                            shared_trips.append(st_check)
                    t_check =  {'id': user_trips[i].trip_id, 'destination': user_trips[i].destination, 'start_date': str(user_trips[i].start_date), 'end_date': str(user_trips[i].end_date), 'is_shared': user_trips[i].is_shared}
                    if t_check not in archived_trips:
                        ut_final.append(t_check)

                        
            elif st_len > ut_len:
                for i in range(st_len):
                    if i < ut_len:
                        t_check = {'id': user_trips[i].trip_id, 'destination': user_trips[i].destination, 'start_date': str(user_trips[i].start_date), 'end_date': str(user_trips[i].end_date), 'is_shared': user_trips[i].is_shared}
                        if t_check not in archived_trips and t_check is not None:
                            ut_final.append(t_check)
                    st_check = {'id': shared_trips_items[i].trip.trip_id, 'destination': shared_trips_items[i].trip.destination, 'start_date': str(shared_trips_items[i].trip.start_date), 'end_date': str(shared_trips_items[i].trip.end_date), 'is_shared': shared_trips_items[i].trip.is_shared}
                    if st_check not in archived_trips:
                        shared_trips.append(st_check)
        
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                location = data.get('location')
                start_date = data.get('start_date')
                end_date = data.get('end_date')

                trip_id = generate_random_digits_large()

                trip = Trip.objects.create(
                    user=request.user,
                    destination=location,
                    start_date=start_date,
                    end_date=end_date,
                    trip_id=trip_id
                )

                trip.save()
                
                Budget.objects.create(
                    budget_id = generate_random_digits_large(),
                    user = request.user,
                    trip = trip,
                    total_amount = 10_000,
                    currency = 'USD'
                )

                tot.append({'id': trip_id, 'destination': location, 'start_date': str(start_date), 'end_date': str(end_date), 'is_shared': False})
                print(f'This is tot: {tot}')
            except:
                pass
        user_profile = UserProfile.objects.get(user=request.user)
        current_total = json.loads(user_profile.total) if user_profile.total else []
        current_total.extend(tot)
        current_total.extend(ut_final)
        current_total.extend(shared_trips)
        tot = sorted(current_total, key=itemgetter('start_date'))
        print(f'This is tot {tot}')
        UserProfile.objects.filter(user=request.user).update(total=json.dumps(tot))
        try:
            all_trips = json.loads(user_profile.total)
            total_trips = len(all_trips)
            trt = []
            brt = []

            for i, trip in enumerate(all_trips):
                if i % 2 == 0:
                    trt.append(trip)
                else:
                    brt.append(trip) 
            UserProfile.objects.filter(user=request.user).update(trt=json.dumps(trt))
            UserProfile.objects.filter(user=request.user).update(brt=json.dumps(brt))
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
 
        #UserProfile.objects.filter(user=request.user).update(trt=json.dumps(trt), brt=json.dumps(brt))
        print(f'This is trt {trt}')
        print(f'This is brt {brt}')

        updated_profile = UserProfile.objects.get(user=request.user)
        context = {
            'trt': trt,
            'brt': brt,
            'archived_trips': archived_trips,
            'notify': new_notification(request.user),
        }
        shared_trips = []
        ut_final = []
    # YOU WILL NEED 2 LISTS FOR THE TRIPS
        # ONE LIST FOR THE TOP ROW
        # ONE LIST FOR THE BOTTOM ROW
        # The len of the top row list should be either 0 and 1 greater than the len of the bottom row

    return render(request, 'main/overview.html', context)


def checklist(request):
    return render(request, 'main/checklist.html')


def autocomplete(request):
    city = request.GET.get('city')
    if not city:
        return JsonResponse({'status': 400, 'error': 'City parameter is required'})

    city_objs_start_with = City.objects.filter(city__istartswith=city)
    city_objs_contain = City.objects.filter(city__icontains=city).exclude(city__istartswith=city)

    payload = [(city_obj.city,city_obj.country) for city_obj in city_objs_start_with] + \
              [(city_obj.city,city_obj.country) for city_obj in city_objs_contain]

    return JsonResponse({'status': 200, 'data': payload})


def search_bar(request):
    return render(request, 'main/autocomplete.html')


def pexel(request):
    return render(request, 'main/pexelphotos.html')