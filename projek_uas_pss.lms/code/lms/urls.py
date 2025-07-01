# simplelms/urls.py
from django.contrib import admin
from django.urls import path
from lms_core.views import (
    index,
    GetProfileView, 
    UpdateProfileView, 
    CourseListView, 
    CreateCourseAnnouncementView, 
    UpdateCourseAnnouncementView, 
    DeleteCourseAnnouncementView, 
    ShowCourseAnnouncementView, 
    AddCategoryView, 
    ShowCategoryView, 
    DeleteCategoryView, 
    AddBookmarkView, 
    ShowBookmarksView, 
    DeleteBookmarkView, 
    ShowCourseContentView,
    RegisterView,
    BatchEnrollView,
    UserListView
)
from rest_framework_simplejwt import views as jwt_views  # Tambahkan ini untuk JWT views

urlpatterns = [
    path('', index),
    path('api/users/', UserListView.as_view(), name='user-list'),
    # JWT Authentication Endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('api/login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Untuk mendapatkan token
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),  # Untuk me-refresh token
    
    # API Routes
    path('api/v1/contents/', ShowCourseContentView.as_view()),
    path('api/batch-enroll/', BatchEnrollView.as_view(), name='batch-enroll'),
    path('api/v1/profile/', GetProfileView.as_view(), name="get-profile"),
    path('api/v1/profile/update/', UpdateProfileView.as_view(), name="update-profile"),
    path('api/v1/courses/', CourseListView.as_view(), name="course-list"),
    path('api/v1/courses/<int:course_id>/announcements/', ShowCourseAnnouncementView.as_view(), name="show-course-announcement"),
    path('api/v1/courses/<int:course_id>/announcements/create/', CreateCourseAnnouncementView.as_view(), name="create-course-announcement"),
    path('api/v1/announcements/<int:announcement_id>/update/', UpdateCourseAnnouncementView.as_view(), name="update-course-announcement"),
    path('api/v1/announcements/<int:announcement_id>/delete/', DeleteCourseAnnouncementView.as_view(), name="delete-course-announcement"),
    path('api/v1/categories/add/', AddCategoryView.as_view(), name="add-category"),
    path('api/v1/categories/', ShowCategoryView.as_view(), name="show-categories"),
    path('api/v1/categories/<int:category_id>/delete/', DeleteCategoryView.as_view(), name="delete-category"),
    path('api/v1/bookmarks/add/', AddBookmarkView.as_view(), name="add-bookmark"),
    path('api/v1/bookmarks/', ShowBookmarksView.as_view(), name="show-bookmarks"),
    path('api/v1/bookmarks/<int:bookmark_id>/delete/', DeleteBookmarkView.as_view(), name="delete-bookmark"),

    
    # Admin Panel
    path('admin/', admin.site.urls),
    path('', index),
]
