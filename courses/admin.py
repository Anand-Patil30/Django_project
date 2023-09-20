from django.contrib import admin
from courses.models import Course,Tag,Learning,Prerequisites,Video,Payment,UserCourse,User,Rating

class TagAdmin(admin.TabularInline):
    model=Tag
class LearningAdmin(admin.TabularInline):
    model=Learning
class PrerequisitesAdmin(admin.TabularInline):
    model=Prerequisites
class VideoAdmin(admin.TabularInline):
    model=Video
class RatingAdmin(admin.TabularInline):
    model=Rating

class CourseAdmin(admin.ModelAdmin):
    inlines=[TagAdmin,LearningAdmin,PrerequisitesAdmin,VideoAdmin,RatingAdmin]


admin.site.register(Course,CourseAdmin)
admin.site.register(Video)
admin.site.register(Payment)
admin.site.register(UserCourse)
admin.site.register(User)
admin.site.register(Rating)