from rest_framework import serializers
from .models import *

class CourseSerializers(serializers.ModelSerializer):
    class Meta:
        model=Course
        fields='__all__'
        

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model=Course
        

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        

class videoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Video
        

class UserCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserCourse
        

class Rating(serializers.ModelSerializer):
    class Meta :
        model =Rating
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('email','password','role')


class VideoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Video
        fields='__all__'

class UserCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserCourse
        fields='__all__'
