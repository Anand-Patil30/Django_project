from optparse import Option
from django.shortcuts import render,redirect
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
