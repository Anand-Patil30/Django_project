import base64
import hashlib
import hmac
from optparse import Option
from django.shortcuts import render,redirect
import requests
from .models import User, Video
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
import random
from django.http import HttpResponse
from .forms import SearchForm, UserLoginForm,UserRegistrationForm
from django.shortcuts import render,redirect
from .models import Course, Tag, Prerequisites, Learning,Payment,Rating
from .forms import CourseForm, TagForm, PrerequisitesForm, LearningForm,VideoForm
from django.contrib.auth.decorators import login_required
from courses.models import Course,Video,Payment,UserCourse
from OLP.settings import *
from time import time
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
import razorpay
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .decorators import student_required,teacher_required
from django.core.paginator import Paginator
from django.db.models import Avg




@student_required
def index(request):
        courses=Course.objects.get_queryset().order_by('id')
        paginator = Paginator(courses, 3) 
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context={
                'page_obj':page_obj}
        return render(request,'courses/student_dash.html', context=context)
    
def enrolled_courses(request):
    user=request.user
    user_course=UserCourse.objects.filter(user=user)
    return render(request,'courses/enrollerd_courses.html',{'user_course':user_course})

def login_view(request):
    errors = {}
    if request.method == "POST":
        form = UserLoginForm(request.POST)  
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            role = form.cleaned_data.get("role")
            try:
                username = User.objects.get(email=email, role=role).username
            except:
                try:
                    username = User.objects.get(email=email)
                    errors["invalid_role"] = "Selected role not associated with this email"
                    return render(request, "courses/login.html", {"form": form, "errors": errors})
                except User.DoesNotExist:
                    errors["bad_credentials"] = "Invalid Email / Password"
                    return render(request, "courses/login.html", {"form": form, "errors": errors})
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.role == role:
                    request.session["username"] = username
                    request.session["role"] = role
                    email = form.cleaned_data['email']
                    otp = ''.join(random.choices('0123456789', k=6))
                    request.session['otp'] = otp
                    send_mail(
                        'OTP Verification',
                        f'Your OTP is: {otp}',
                        'patilanand342@gmail.com',
                        [email],
                        fail_silently=False,
                    )
                    login(request, user) 
                    return redirect('otp_verification')
                else:
                    errors["invalid_role"] = "Selected role not associated with this email"
                    return render(request, "courses/login.html", {"form": form, "errors": errors})
            else:
                errors["bad_credentials"] = "Invalid Email / Password"
                return render(request, "courses/login.html", {"form": form, "errors": errors})
        else:
            errors["invalid_data"] = "Invalid form data. Please try again."
            return render(request, "courses/login.html", {"form": form, "errors": errors})
    else:
        form = UserLoginForm()
        errors = {}
    return render(request, "courses/login.html", {"form": form, "errors": errors})


def otp_verification_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('otp'):
            role = request.session.get('role')
            if role == 'student':   
                return redirect('base')  
            elif role == 'teacher':
                return redirect('display')   
        else:
            errors = {'invalid_otp': 'Invalid OTP. Please try again.'}
            return render(request, 'courses/otp_verification.html', {'errors': errors})
    return render(request, 'courses/otp_verification.html')


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            errors = form.errors
    else:
        form = UserRegistrationForm()
    errors = None
    return render(request, "courses/signup.html", {"form": form, "errors": errors})


@teacher_required
def add_course(request):
    if request.method == 'POST':
        user = request.user
        courses = Course.objects.filter(teacher=user)

        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = user
            course.save()
            enrolled_student_emails = Payment.objects.filter(course__in=courses).values_list('user__email', flat=True).distinct()
            if enrolled_student_emails:
                email_subject = 'New Course Notification!'
                from_email = 'patilanand342@gmail.com'
                to_email_list = list(enrolled_student_emails)
                
                send_mail(
                    email_subject,
    f'''Dear [Student's Name],

        I hope this email finds you well. We are thrilled to welcome you to {course} at Online learning platform 
        Your decision to register for this course is an exciting step towards your academic and personal growth,
        and we are here to support you throughout this journey.
        
        {course } is designed to provide you with a comprehensive understanding of [Course Topic].
        Whether you are pursuing this course to further your career, gain new skills, or simply explore a subject of interest,
        we are committed to ensuring you have a rewarding and enriching experience.
        
        If you have any questions or need assistance with any aspect of the course, 
        please don't hesitate to reach out to us at [Contact Email] or [Contact Phone Number]. 
        Our dedicated support team is here to help.

        We wish you the very best as you embark on this educational journey with us. 
        Prepare to be inspired, challenged, and engaged in {course}. 
        We look forward to seeing you on 30/02/2024!
        
        
    
    Regards Team OLP''',
                    from_email,
                    to_email_list,
                    fail_silently=False,
                )

            return redirect('display')
    else:
        form = CourseForm()
    return render(request, 'courses/add_course.html', {'form': form})

# def add_course(request):
#     if request.method == 'POST':
#         user=request.user
#         courses=Course.objects.filter(teacher=user)
#         form = CourseForm(request.POST,request.FILES)
#         if form.is_valid():
#             course= form.save(commit=False)
#             course.teacher=user
#             course.save()
#             list1=[]
#             for course in courses:
#                 enrolled_student_id=Payment.objects.filter(course=course).values_list('user',flat=True)
#                 enrolled_student=User.objects.filter(id__in=enrolled_student_id)
#                 for student in enrolled_student:
#                     email=student.email
#                     if email not in list1:
#                         list1.append(email)
#             print(list1)
#             for mail in list1:
#                 send_mail(
#                         'New Course Notification!',
#                         f'''
#             Dear Student,
#             {user} has added a new Course check out newly added Course {course}
#             ''',
#                         'patilanand342@gmail.com',
#                         [mail],
#                         fail_silently=False,
#                         )
#             return redirect('display')
#     else:
#         form = CourseForm()
#     return render(request, 'courses/add_course.html', {'form': form})

def show_course(request,slug):
    course=get_object_or_404(Course,slug=slug)
    serial_number=request.GET.get('lecture')
    videos=course.video_set.all().order_by('serial_number')
    if serial_number is None:
        serial_number=1
    video=Video.objects.get(serial_number=serial_number,course=course)
    context={
        'course':course,
        'videos':videos,
        'video':video
    }    
    return render(request,'courses/show_course.html',context) 


def delete_course(request,id):
    content=get_object_or_404(Course,id=id)
    content.delete()
    return redirect('display')


def update_course(request,id):
    content=get_object_or_404(Course,id=id)
    if request.method=="POST":
        form=CourseForm(request.POST,instance=content)
        if form.is_valid():
            form.save()
            return redirect('display')
    else:
        form=CourseForm(instance=content)
    return render(request,'courses/update_course.html',{'form':form})        

# @login_required(login_url='login')
# def add_tag(request):
#     if request.method == 'POST':
#         form = TagForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('display')
#     else:
#         form = TagForm()
#     return render(request, 'courses/add_tag.html', {'form': form})

# @login_required(login_url='login')
# def add_prerequisites(request):
#     if request.method == 'POST':
#         form = PrerequisitesForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('display')
#     else:
#         form = PrerequisitesForm()
#     return render(request, 'courses/add_prerequisites.html', {'form': form})

# @login_required(login_url='login')
# def add_learning(request):
#     if request.method == 'POST':
#         form = LearningForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('display')
#     else:
#         form = LearningForm()
#     return render(request, 'courses/add_learning.html', {'form': form})

@teacher_required
def add_video(request,id):
    course=Course.objects.get(id=id)
    user=request.user
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video=form.save(commit=False)
            video.course=course
            video.save()
            enrolled_students_emails=UserCourse.objects.filter(course=course).values_list('user__email',flat=True)
            content=video.title
            
            if enrolled_students_emails:
                email_subject = 'New Course Notification!'
                from_email = 'patilanand342@gmail.com'
                to_email_list = list(enrolled_students_emails)
                
                send_mail(
                    email_subject,
    f'''Dear Student,
    
            {user} has added new Contents to The Course {course}
            Check Out the latest Content:{content}
            
        
    Regards Team OLP''',
                    from_email,
                    to_email_list,
                    fail_silently=False,
                )
            return redirect('view_video',id=course.id)
    else:
        form = VideoForm()
        context={'form': form,
                'course':course}
    return render(request, 'courses/add_video.html',context)

def view_video(request,id):
    course=Course.objects.get(id=id)
    video=Video.objects.filter(course=course).order_by('serial_number')
    context={
            'video':video,
            'course':course}
    return render(request, 'courses/show_content.html',context)

def Update_content(request,id):
    content=get_object_or_404(Video,pk=id,course__teacher=request.user) 
    if request.method=="POST":
        form=VideoForm(request.POST,instance=content)
        if form.is_valid():
            form.save()
            return redirect('view_video',id=content.course.id)
    else:
        form=VideoForm(instance=content)
    context={
        'form':form,
        'content':content
    }
    return render(request,'courses/update.html',context)

def delete_content(request,id):
    video= get_object_or_404(Video, pk=id ,course__teacher=request.user)
    print(video.id)
    video.delete()
    print(video.course.id)
    return redirect('view_video',id=video.course.id)


@teacher_required
def display(request):
    user=request.user
    course=Course.objects.filter(teacher=user).order_by('id')
    # tag=Tag.objects.all()
    # prerequisites=Prerequisites.objects.all()
    # learning=Learning.objects.all()
    # video=Video.objects.all()
    paginator = Paginator(course, 3) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context={
        'page_obj':page_obj
    }
    return render(request, 'courses/display.html', context)




client=razorpay.Client(auth=(key_id,key_secret))

@student_required
def checkout(request,slug):
    course=Course.objects.get(slug=slug)
    user=request.user
    error=None
    amount=int((course.price - (course.price * course.discount * 0.01))*100)
    currency="INR"
    notes={
            "email":user.email,
            "name":f'{user.username}'
            }
    receipt= f"Online Learning Platform -{int(time())}"
    
    order=client.order.create(
            {'receipt':receipt,
            'notes':notes,
            'amount':amount,
            'currency':currency
            })

    print("ORDER: ", order)
    payment=Payment()
    payment.user=user
    payment.course=course
    payment.order_id=order.get('id')
    payment.status = order.get('status')
    payment.save()

    context={
        "course":course,
        "order":order,
        "payment":payment,
        "user":user,
        "error":error
    }
    return render(request,template_name='courses/checkout.html',context=context)

@csrf_exempt   
def verifyPayment(request):
    if request.method == "GET":
        data = request.GET
        context = {}
        
        try:
            razorpay_order_id = data['order_id']
            razorpay_payment_id = data['payment_id']
            print(data)
            print(razorpay_order_id)
            print(razorpay_payment_id)
            
            payment = Payment.objects.get(order_id=razorpay_order_id)
            
            payment.payment_id = razorpay_payment_id
            payment.status = "success"

            userCourse = UserCourse.objects.create(user=payment.user, course=payment.course)
            payment.user_course = userCourse
            payment.save()

            subject = 'Course Enrollment Confirmation'
            message = f"Thank you for enrolling in the course '{payment.course.name}'."
            from_email = 'patilanand342@gmail.com'  
            to_email = payment.user.email
            email = EmailMessage(subject, message, from_email, [to_email])
            email.send()
            return redirect('base')
        
        except razorpay.errors.SignatureVerificationError as e:
            return HttpResponse("Invalid Payment details: Signature Verification Error")
        except Payment.DoesNotExist:
            print(request.user.username)
            return HttpResponse("Invalid Payment details: Payment not found")


def signout(request):
    logout(request)
    return redirect('login')


def search_view(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Course.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
            return render(request, 'courses/search_results.html', {'results': results})
    else:
        form = SearchForm()
    return render(request, 'courses/search_results.html', {'form': form})

@teacher_required
def enrolled_students(request,id):
    course=Course.objects.get(id=id)
    enrolled_student_id=Payment.objects.filter(course=course).values_list('user',flat=True)
    enrolled_student=User.objects.filter(id__in=enrolled_student_id)
    
    context={
        'course':course,
        'enrolled_student':enrolled_student
    }
    return render(request,'courses/enrolled_students.html',context)



def rating(request,slug):
    if request.method == 'POST' and request.user.is_authenticated:
        rating_value = int(request.POST.get('rating'))
        course = get_object_or_404(Course, slug=slug)
        existing_rating = Rating.objects.filter(user=request.user, course=course).first()

        if existing_rating:
            existing_rating.rate = rating_value
            existing_rating.save()
        else:
            Rating.objects.create(user=request.user,course=course,rate=rating_value)
    return redirect('show_course', slug=slug)



def filter_courses(request):
    rating = request.GET.get('rating')
    price = request.GET.get('price')
    courses = Course.objects.all()
    
    if rating:
        courses = courses.annotate(avg_rating=Avg('rating__rate'))
        courses = courses.filter(avg_rating=rating)

    if price:
        if price == 'free':
            courses = courses.filter(price=0)
        elif price == 'paid':
            courses = courses.exclude(price=0)
            
    print(courses)

    return render(request, 'courses/filter_list.html',{'courses': courses} )




####################################   API   #######################################




from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.utils.crypto import get_random_string
from django.shortcuts import render,redirect
from django.urls import path,include
from django.shortcuts import HttpResponse
from courses.models import Course
from django.contrib.auth import logout,login
from courses.models import User
from django.contrib.auth import login, authenticate
from courses.forms import UserRegistrationForm,UserLoginForm
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from courses.models import User
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from courses.custom_permissions import StudentRolePermission,TeacherRolePermission
from courses.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from courses.serializers import UserRegistrationSerializer
from courses.models import User

class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            role = serializer.validated_data.get("role")

            
            if User.objects.filter(email=email).exists():
                return Response({"detail": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            user.save()

            return Response({"detail": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from courses.serializers import UserLoginSerializer
from django.contrib.auth import authenticate

class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            role = serializer.validated_data.get("role")
            username = User.objects.get(email=email, role=role).username
            print(username)

            user = authenticate(request, username=username, password=password)
            print(user)

            if user is not None and user.role == role:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                return Response({"access_token": access_token,"refresh_token":refresh_token}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([TeacherRolePermission])
def user_logout(request):
    try:
        refresh_token = request.data['refresh_token']
    except KeyError:
        return Response({"detail": "Refresh token is required for logout."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  
    except Exception as e:
        return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([StudentRolePermission])
def student_logout(request):
    try:
        refresh_token = request.data['refresh_token']
    except KeyError:
        return Response({"detail": "Refresh token is required for logout."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  
    except Exception as e:
        return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializers

@api_view(['POST'])
@permission_classes([TeacherRolePermission])
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.data)
        if form.is_valid():
            course = form.save(commit=False)
            # course.added_by = request.user
            course.save()
            serializer = CourseSerializers(course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


from courses.serializers import UserSerializer 
@api_view(['GET'])
@permission_classes([TeacherRolePermission])
def purchased_students_api(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"detail": "Course not found"}, status=404)
    purchased_students_ids = Payment.objects.filter(course=course).values_list('user', flat=True)
    purchased_students = User.objects.filter(id__in=purchased_students_ids,role='student')
    serializer = UserSerializer(purchased_students, many=True)
    return Response(serializer.data, status=200)


#####--------check out --------####

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from courses.custom_permissions import StudentRolePermission
from courses.serializers import CourseSerializers,UserSerializer,PaymentSerializer

@api_view(['GET'])
@permission_classes([StudentRolePermission])
def checkout_api(request, slug):
    client = razorpay.Client(auth=(key_id, key_secret))
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    action = request.GET.get('action')
    order = None
    error = None
    payment = None

    try:
        user_course = UserCourse.objects.get(user=user, course=course)
        error = "You are already enrolled in this course"
    except UserCourse.DoesNotExist:
        pass

    if error is None:
        amount = int((course.price - (course.price * course.discount * 0.01)) * 100)
        currency = "INR"
        notes = {
            "email": user.email,
            "name": f'{user.username}'
        }
        receipt = f"onlinelearning-{int(time())}"
        order = client.order.create(
            {
                'receipt': receipt,
                'notes': notes,
                'amount': amount,
                'currency': currency
            })

        payment = Payment()
        payment.user = user
        payment.course = course
        payment.order_id = order.get('id')
        payment.status = 'created'
        payment.save()
    course_serializer= CourseSerializers(course)
    user_serializer=UserSerializer(user)
    payment_serializer=PaymentSerializer(payment)
    context={
        "course":course_serializer.data,
        "order":order,
        "payment":payment_serializer.data,
        "user":user_serializer.data,
        "error":error

    }
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
def verify_payment_api(request):
    if request.method == "GET":
        data = request.GET
        print(data)
        context = {}

        try:
            razorpay_order_id = data['order_id']
            razorpay_payment_id = data['payment_id']
            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.status = "success"
            user_course = UserCourse.objects.create(user=payment.user, course=payment.course)
            payment.user_course = user_course
            payment.save()

            subject = 'Course Enrollment Confirmation'
            message = f"Thank you for enrolling in the course '{payment.course.name}'."
            from_email = 'patilanand342@gmail.com'
            to_email = payment.user.email
            email = EmailMessage(subject, message, from_email, [to_email])
            email.send()

            return Response({'detail': 'Payment successful'}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError as e:
            return Response({'detail': 'Invalid Payment details: Signature Verification Error'}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'detail': 'Invalid Payment details: Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        

from django.conf import settings
@api_view(['POST'])
@permission_classes([StudentRolePermission])
def payment(request):
    order_id = request.data.get('order_id')
    print(order_id)
    razorpay_key_id = settings.key_id
    razorpay_key_secret = settings.key_secret
    auth_header_encoded = f"Basic {base64.b64encode(f'{razorpay_key_id}:{razorpay_key_secret}'.encode()).decode()}"
    headers_encoded = {
        "Authorization": auth_header_encoded
    }

    order_data = requests.get(f"https://api.razorpay.com/v1/orders/{order_id}", headers=headers_encoded)
    data = order_data.json()
    print(data)
    payment_data = {
        "order_id": order_id,
        "amount": data["amount"],                     
        "email": "swaroopbhat12345@gmail.com",
        "contact": "7899095676",
        "currency": data["currency"],
        "method": "upi",
        "upi": {
            "flow": "collect",
            "type": "default",
            "vpa": "success@razorpay",  
            "vpa_name": "Swaroop bhat", 
            "payer_vpa": "success@razorpay",  
            "payer_name": "Swaroop bhat",  
        }
    }

    auth_header = f"{razorpay_key_id}:{razorpay_key_secret}"
    headers = {
        "Authorization": auth_header
    }
    create_payment_response = requests.post("https://api.razorpay.com/v1/payments", json=payment_data, headers=headers)
    order_response = requests.get(f"https://api.razorpay.com/v1/orders/{order_id}/payments", headers=headers_encoded)
    order_data = order_response.json()
    print("ORDER DATA: ", order_data)
    if order_data.get("count") == 0:
        return Response({"message": "Payment creation failed"}, status=status.HTTP_400_BAD_REQUEST) 
    else:
        payment_id = order_data.get("items")[0].get("id") 

    if order_data.get("items")[0].get("status") == "captured":
        data_to_sign = order_id + "|" + payment_id
        generated_signature = hmac.new(razorpay_key_secret.encode(), data_to_sign.encode(), hashlib.sha256).hexdigest()
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        signature = client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': generated_signature
        })
        if signature:
            try:
                payment = Payment.objects.get(order_id = order_id)
            except:
                return Response({'error':'Invalid Order Id for the course '}, status=status.HTTP_400_BAD_REQUEST)
            payment.status = 'success'
            payment.payment_id = payment_id
            payment.save()
            student_email = request.user.email
            subject_student = "Thank You for Your Purchase"
            message_student = f"Congratulations on your successful purchase! Your payment has been processed. \n Please find below the details to access your purchase: \n Order ID: {order_id} \n "
            return Response({"message": "Your payment is successful"}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid Signature'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Payment not Successful, try again"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([StudentRolePermission])
def my_courses_list_api(request):
    user_courses = UserCourse.objects.filter(user=request.user)
    serializer = UserCourseSerializer(user_courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([StudentRolePermission])
def course_page_api(request, slug):
    course = get_object_or_404(Course, slug=slug)
    serial_number = request.GET.get('lecture')
    videos = Video.objects.filter(course=course).order_by("serial_number")

    if serial_number is None:
        serial_number = 1

    video = get_object_or_404(Video, serial_number=serial_number, course=course)

    if not video.is_preview:
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            user = request.user
            try:
                user_course = UserCourse.objects.get(user=user, course=course)
            except UserCourse.DoesNotExist:
                return Response({"detail": "Course not purchased"}, status=status.HTTP_403_FORBIDDEN)

    course_serializer = CourseSerializers(course)
    video_serializer = videoSerializer(video)
    videos_serializer = videoSerializer(videos, many=True)

    context = {
        "course": course_serializer.data,
        "video": video_serializer.data,
        "videos": videos_serializer.data
    }
    return Response(context, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([TeacherRolePermission])
def display_course_details_api(request):
    user = request.user
    courses = Course.objects.filter(added_by=user)
    course_serializer = CourseSerializers(courses, many=True)

    context = {
        'courses': course_serializer.data
    }
    return Response(context, status=status.HTTP_200_OK)




@api_view(['DELETE'])
@permission_classes([TeacherRolePermission])
def delete_course_api(request, course_id):
    course = get_object_or_404(Course, id=course_id, added_by=request.user)
    if request.method == 'DELETE':
        course.delete()
        return Response({"message": "Course deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    


@api_view(['PUT'])
@permission_classes([TeacherRolePermission])
def update_course_api(request, course_id):
    course = get_object_or_404(Course, id=course_id, added_by=request.user)

    if request.method == 'PUT':
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from courses.serializers import videoSerializer

@api_view(['POST', 'GET'])
@permission_classes([TeacherRolePermission])
def add_content_api(request, course_id):
    course = get_object_or_404(Course, id=course_id, added_by=request.user)

    if request.method == 'POST':
        serializer = videoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save(course=course)

            purchased_users = User.objects.filter(usercourse__course=course)
            subject = 'New Content Added to {}'.format(course.name)
            message = 'New content has been added to the course: {}\n\nVisit the course page to see the new content.'.format(course.name)
            from_email = 'swaroopbhat12345@gmail.com' 
            recipient_list = [user.email for user in purchased_users]

            send_mail(subject, message, from_email, recipient_list)

            return Response({"message": "Content added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        content = Video.objects.filter(course=course)
        serializer = videoSerializer(content, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




from courses.serializers import VideoUpdateSerializer
@api_view(['GET', 'PUT'])
@permission_classes([TeacherRolePermission])
def update_video_api(request, video_id):
    video = get_object_or_404(Video, id=video_id, course__added_by=request.user)

    if request.method == 'GET':
        serializer = VideoUpdateSerializer(video)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = VideoUpdateSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([TeacherRolePermission])
def delete_video_api(request, video_id):
    video = get_object_or_404(Video, id=video_id, course__added_by=request.user)

    if request.method == 'DELETE':
        video.delete()
        return Response({"message": "Video deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([StudentRolePermission])
def course_list(request):
    data = Course.objects.all()
    serializer = CourseSerializers(data, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def search_courses(request):
    query = request.GET.get('q')
    if query:
        courses = Course.objects.filter(Q(name__iexact=query))
        serializer = CourseSerializers(courses, many=True)
        return Response(serializer.data)
    else:
        return Response([])
    
    

@api_view(['POST'])
@permission_classes([StudentRolePermission])
def rate_course_api(request, slug):
    rating_value = int(request.data.get('rating', 0))
    course = get_object_or_404(Course, slug=slug)
    existing_rating = Rating.objects.filter(user=request.user, course=course).first()
    if existing_rating:
        existing_rating.rating = rating_value
        existing_rating.save()
    else:
        Rating.objects.create(
            user=request.user,
            course=course,
            rating=rating_value
        )
    return Response({"message": "Course rated successfully"}, status=status.HTTP_200_OK)



@api_view(['POST'])
def forgot_password_api(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        token = get_random_string(length=40)
        user.reset_token = token
        user.save()
        reset_link = request.build_absolute_uri(f'/reset-password/{token}/')
        send_reset_email(email, reset_link)
        return Response({'detail': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password_api(request, token):
    try:
        user = User.objects.get(reset_token=token)
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        if len(new_password) >= 8:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.reset_token = None
                user.save()
                return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

def send_reset_email(email, reset_link):
    subject = 'Password Reset'
    message = f'Click the following link to reset your password: {reset_link}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

