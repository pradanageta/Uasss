from django.contrib import admin
from lms_core.models import Course, CourseContent

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "description", "teacher", 'created_at']
    list_filter = ["teacher"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "description", "price", "image", "teacher", "created_at", "updated_at"]

@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ["name", "course_id", "video_url", "created_at"]
    list_filter = ["course_id"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "description", "video_url", "file_attachment", "course_id", "parent_id", "created_at", "updated_at"]