from django import views
from django.conf import settings
from django.contrib import admin
from django.urls import path
from .views import *
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

]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)