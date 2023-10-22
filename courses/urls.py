from django import views
from django.conf import settings
from django.contrib import admin
from django.urls import path
from .views import *
from .serializers import *
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("",index,name="base"),
    path("login/",login_view,name="login"),
    path("signup/",register_view,name="signup"),
    path("otp_verification/",otp_verification_view,name="otp_verification"),
    path("add_video/<int:id>",add_video),
    # path("add_learning/",add_learning,name="add_learning"),
    # path("add_prerequisites/",add_prerequisites,name="add_prerequisites"),
    # path("add_tag/",add_tag,name="add_tag"),
    path("add_course/",add_course,name="add_course"),
    path("delete_course/<int:id>",delete_course,name="delete_course"),
    path("update_course/<int:id>",update_course,name="update_course"),
    path("display/",display,name="display"),
    path("checkout/<str:slug>",checkout,name="checkout"),
    path("verify_payment/",verifyPayment,name="verify_payment"),
    path("show_course/<str:slug>",show_course,name="show_course"),
    path("logout/", signout,name="logout"),
    path("update/<str:id>", Update_content),
    path("view_video/<int:id>", view_video,name="view_video"),
    path("delete_content/<int:id>", delete_content,name="delete_content"),
    path('filter/', filter_courses, name='filter_courses'),
    path('search/', search_view, name='search'),
    path('rating/<str:slug>', rating, name='rating'),
    path('enrolled_students/<int:id>', enrolled_students, name='enrolled_students'),
    path('enrolled_courses', enrolled_courses, name='enrolled_courses'),
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='courses/password_reset.html'),name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='courses/password_reset_confirm.html'),name='password_reset_confirm'),    
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='courses/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='courses/password_reset_complete.html'),name='password_reset_complete'),


###############################  API Urls   ###############################
   
    path('api/gettoken/',TokenObtainPairView.as_view(),name="gettoken"),
    path('api/refreshtoken/',TokenRefreshView.as_view(),name="refreshtoken"),
    path('api/verifytoken/',TokenVerifyView.as_view(),name="verify"),



    path('api/registration/',UserRegistrationAPIView.as_view(),name="userregistration"),
    path('api/login/',UserLoginAPIView.as_view(),name='api_login'),
    path("api/courselist/",course_list,name="api_courselist"),
    path("api/addcourse/",add_course,name="api_addcourse"),
    path('api/display-course-details/',display_course_details_api,name='display_course_details_api'),
    path('api/courses/<int:course_id>/purchased-students/', purchased_students_api, name='purchased-students-api'),
    path('api/user/logout/', user_logout, name='user-logout'),
    path('api/student/logout/',student_logout,name='student_logout'),
    path('api/courses/<int:course_id>/add_content/',add_content_api,name='api_content'),
    path('api/videos/<str:video_id>/',update_video_api,name='api_update'),
    path('api/videos/delete/<int:video_id>/', delete_video_api, name='delete-video-api'),
    path('api/course/delete/<int:course_id>/',delete_course_api,name='delete_course_api'),
    path('api/course/update/<int:course_id>/', update_course_api, name='update-course-api'),
    path('api/my-courses/', my_courses_list_api, name='my-courses-api'),
    path('api/course-page/<slug>/', course_page_api, name='course-page-api'),
    path('api/rate-course/<slug>/', rate_course_api, name='rate-course-api'),
    path('api/forgot-password/', forgot_password_api, name='forgot-password-api'),
    path('api/reset-password/<token>/', reset_password_api, name='reset-password-api'),
    path('api/checkout/<slug>/', checkout_api, name='checkout-api'),
    path('api/verify-payment/', verify_payment_api, name='verify-payment-api'),
    path('api/payment_verification/',payment,name='payment_verification'),

]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)