from django.db import models
from courses.managers import CustomUserManager
from django.conf import settings
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,Group,Permission,PermissionsMixin
import uuid
from django.db import models
from PIL import Image
import courses.models


class Course(models.Model):
    name=models.CharField(max_length=50,null=False)
    slug=models.CharField(max_length=50,null=False,unique=True)
    description=models.CharField(max_length=200,null=True)
    price=models.IntegerField(max_length=200)
    discount=models.IntegerField(null=False,default=0)
    active=models.BooleanField(default=True)
    img=models.ImageField(upload_to="files/img")
    date=models.DateTimeField(auto_now_add=True)
    length=models.IntegerField(null=False)
    teacher=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)
        image = Image.open(self.img.path)
        
        if image.width > 300 or image.height > 200 :
            output_size=(300, 200)
            image.thumbnail(output_size)
            image.save(self.img.path)
            
    def average_rating(self):
            ratings = courses.models.Rating.objects.filter(course=self)
            if ratings:
                total_ratings = sum(rating.rate for rating in ratings)
                return total_ratings / len(ratings)
            return 0

class CourseProperty(models.Model):
    description=models.CharField(max_length=100,null=False)
    course=models.ForeignKey(Course,null=False,on_delete=models.CASCADE)

    class Meta:
        abstract=True


class Tag(CourseProperty):
    pass


class Prerequisites(CourseProperty):
    pass


class Learning(CourseProperty):
    pass



class Payment(models.Model):
    order_id=models.CharField(max_length=50,null=False)
    payment_id=models.CharField(max_length=50)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20)
    
    def __str__(self) :
        return f'Payments for Course {self.course} by {self.user}'


class UserCourse(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,null=False,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,null=False,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.course.name}'



class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=120)
    username = models.CharField(unique=True, max_length=120)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def __str__(self):
        return self.username


class Video(models.Model):
    title=models.CharField(max_length=100,null=False)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    serial_number=models.IntegerField(null=False)
    video_id=models.CharField(max_length=100,null=False)
    is_preview=models.BooleanField(default=False)


    def __str__(self):
        return self.title


class Rating(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    rate=models.IntegerField(choices=[(i,i)for i in range(1,6)])
    created_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)