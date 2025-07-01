# lms_core/views.py
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from lms_core.models import (
    Course, Profile, CourseAnnouncement, Category, CourseContent, Bookmark, CourseMember
)
from rest_framework import status 
from lms_core.serializers import (
    CourseSerializer,
    UserProfileSerializer,
    CourseAnnouncementSerializer,
    CategorySerializer,
    BookmarkSerializer,
    CourseContentSerializer,
    RegisterSerializer,
    BatchEnrollSerializer,
    UserListSerializer
)
from django.contrib.auth.models import User
from .permissions import IsTeacher, IsStudentOrTeacher, IsStudent

def index(request):
    return HttpResponse("<h1>Welcome to Simple LMS API</h1>")

class IndexView(APIView):
    def get(self, request):
        return Response({"message": "Hello World"})

class UserListView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)

class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            print("Error: ", str(e))  # Menambahkan print untuk log
            return Response({"message": "Error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BatchEnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ✅ Validasi role pengguna saat ini
        try:
            if request.user.profile.role != 'teacher':
                return Response(
                    {"error": "Hanya teacher yang diizinkan."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profil pengguna tidak ditemukan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Validasi input
        serializer = BatchEnrollSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            student_ids = serializer.validated_data['student_ids']

            # ✅ Cek apakah course milik teacher ini
            try:
                course = Course.objects.get(id=course_id, teacher=request.user)
            except Course.DoesNotExist:
                return Response(
                    {"error": "Kursus tidak ditemukan atau bukan milik Anda."},
                    status=status.HTTP_404_NOT_FOUND
                )

            added_students = []
            not_found = []
            invalid_role = []

            # ✅ Loop semua student_ids yang dikirim
            for student_id in student_ids:
                try:
                    student = User.objects.get(id=student_id)

                    try:
                        if student.profile.role != 'student':
                            invalid_role.append(student.username)
                            continue
                    except Profile.DoesNotExist:
                        invalid_role.append(student.username)
                        continue

                    member, created = CourseMember.objects.get_or_create(
                        course_id=course,
                        user_id=student,
                        defaults={'roles': 'std'}
                    )

                    if created:
                        added_students.append(student.username)

                except User.DoesNotExist:
                    not_found.append(student_id)

            # ❌ Semua gagal
            if not added_students:
                return Response({
                    "error": "Tidak ada siswa yang berhasil didaftarkan.",
                    "not_found_student_ids": not_found if not_found else None,
                    "user_not_found_message": f"User berikut tidak ditemukan di database: {not_found}" if not_found else None,
                    "invalid_role_usernames": invalid_role if invalid_role else None,
                    "invalid_role_message": f"User berikut bukan siswa: {invalid_role}" if invalid_role else None
                }, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Sebagian atau semua berhasil
            response_data = {
                "message": "Proses batch enroll selesai.",
                "enrolled_students": added_students,
            }

            if not_found:
                response_data["not_found_student_ids"] = not_found
                response_data["user_not_found_message"] = f"User berikut tidak ditemukan di database: {not_found}"

            if invalid_role:
                response_data["invalid_role_usernames"] = invalid_role
                response_data["invalid_role_message"] = f"User berikut bukan siswa: {invalid_role}"

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Buat respons manual
            profile = user.profile if hasattr(user, "profile") else None
            response_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": profile.role if profile else None,
                "phone_number": profile.phone_number if profile else None,
                "description": profile.description if profile else None,
                "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile and profile.profile_picture else None,
            }
            return Response({
                "message": "User registered successfully",
                "user": response_data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        
        # Periksa jika Profile ada, jika tidak buat baru
        try:
            profile = user.profile  # Mengambil Profile terkait User
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        # Ambil data User terlebih dahulu untuk mempermudah referensinya
        user_data = request.data
        first_name = user_data.get('first_name', user.first_name)
        last_name = user_data.get('last_name', user.last_name)
        email = user_data.get('email', user.email)
        
        # Update data User
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()  # Simpan perubahan di User

        # Jika ada perubahan di Profile
        if 'phone_number' in user_data:
            profile.phone_number = user_data['phone_number']
        if 'description' in user_data:
            profile.description = user_data['description']
        if 'profile_picture' in user_data:
            profile.profile_picture = user_data['profile_picture']

        profile.save()  # Simpan perubahan di Profile

        # Serialize and return the response
        serializer = UserProfileSerializer(user)
        return Response({"message": "Profile updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)


class CourseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.all()  # Ambil semua data course
        serializer = CourseSerializer(courses, many=True)  # Gunakan serializer untuk mengonversi queryset ke JSON
        return Response(serializer.data)

class AddCourseView(APIView):
    permission_classes = [IsAuthenticated]  # Menambahkan autentikasi jika diperlukan

    def post(self, request):
        # Menambahkan data course baru
        course_data = request.data
        course = Course(
            name=course_data["name"],
            description=course_data["description"],
            price=course_data["price"],
            teacher=User.objects.get(username=course_data["teacher"]),
        )
        course.save()
        return Response({"message": "Data berhasil ditambahkan"}, status=status.HTTP_201_CREATED)

class EditCourseView(APIView):
    permission_classes = [IsAuthenticated]  # Menambahkan autentikasi jika diperlukan

    def put(self, request):
        # Mengubah data course yang sudah ada
        course_data = request.data
        course = Course.objects.filter(name=course_data["name"]).first()
        if course:
            course.name = course_data["new_name"]
            course.save()
            return Response({"message": "Data berhasil diubah"})
        return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteCourseView(APIView):
    permission_classes = [IsAuthenticated]  # Menambahkan autentikasi jika diperlukan

    def delete(self, request):
        # Menghapus course berdasarkan nama
        course_name = request.data.get("name")
        course = Course.objects.filter(name=course_name).first()
        if course:
            course.delete()
            return Response({"message": "Data berhasil dihapus"})
        return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

class ShowCourseContentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contents = CourseContent.objects.all()
        serializer = CourseContentSerializer(contents, many=True)
        return Response({
            "message": "Konten berhasil diambil",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class CreateCourseAnnouncementView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request, course_id):
        # Hanya Teacher yang bisa membuat announcement
        course = Course.objects.get(id=course_id)
        announcement_data = request.data
        announcement = CourseAnnouncement(
            course=course,
            title=announcement_data['title'],
            content=announcement_data['content'],
            date=announcement_data['date'],
            teacher=request.user  # Menyimpan pengumuman dengan guru yang membuatnya
        )
        announcement.save()
        return Response({"message": "Announcement created successfully"}, status=201)

class ShowCourseAnnouncementView(APIView):
    permission_classes = [IsAuthenticated]  # Memastikan user sudah login

    def get(self, request, course_id):
        # Ambil kursus berdasarkan course_id
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Ambil pengumuman yang terkait dengan kursus ini
        announcements = CourseAnnouncement.objects.filter(course=course)

        # Serialize pengumuman untuk mengubah menjadi JSON
        from lms_core.serializers import CourseAnnouncementSerializer
        serializer = CourseAnnouncementSerializer(announcements, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateCourseAnnouncementView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def put(self, request, announcement_id):
        try:
            # Coba ambil pengumuman berdasarkan ID
            announcement = CourseAnnouncement.objects.get(id=announcement_id)
        except CourseAnnouncement.DoesNotExist:
            # Jika tidak ada pengumuman dengan ID yang diminta, kembalikan error 404
            return Response({"message": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)

        # Verifikasi apakah pengumuman ini milik teacher yang login
        if announcement.teacher != request.user:
            return Response({"message": "You are not allowed to edit this announcement"}, status=403)

        # Update pengumuman
        announcement.title = request.data.get('title', announcement.title)
        announcement.content = request.data.get('content', announcement.content)
        announcement.date = request.data.get('date', announcement.date)
        announcement.save()

        return Response({"message": "Announcement updated successfully"}, status=status.HTTP_200_OK)


class DeleteCourseAnnouncementView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def delete(self, request, announcement_id):
        try:
            # Coba ambil pengumuman berdasarkan ID
            announcement = CourseAnnouncement.objects.get(id=announcement_id)
        except CourseAnnouncement.DoesNotExist:
            # Jika tidak ada pengumuman dengan ID yang diminta, kembalikan error 404
            return Response({"message": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)

        # Verifikasi apakah pengumuman ini milik teacher yang login
        if announcement.teacher != request.user:
            return Response({"message": "You are not allowed to delete this announcement"}, status=403)
        
        # Hapus pengumuman jika semua pengecekan lolos
        announcement.delete()
        return Response({"message": "Announcement deleted successfully"}, status=status.HTTP_200_OK)

class AddCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"message": "Category name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        category = Category.objects.create(name=name)
        return Response({"message": "Category created successfully", "category": {"id": category.id, "name": category.name}}, status=status.HTTP_201_CREATED)

class AddBookmarkView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        # Mengambil data content_id dari request
        content_id = request.data.get('content_id')
        try:
            content = CourseContent.objects.get(id=content_id)
        except CourseContent.DoesNotExist:
            return Response({"message": "Content not found"}, status=status.HTTP_404_NOT_FOUND)

        # Cek apakah student sudah memiliki bookmark untuk konten ini
        if Bookmark.objects.filter(student=request.user, content=content).exists():
            return Response({"message": "Bookmark already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Buat bookmark baru
        bookmark = Bookmark.objects.create(student=request.user, content=content)
        return Response({"message": "Bookmark added successfully", "bookmark": BookmarkSerializer(bookmark).data}, status=status.HTTP_201_CREATED)

class ShowBookmarksView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        # Ambil semua bookmark milik student
        bookmarks = Bookmark.objects.filter(student=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response({"message": "Get bookmarks success", "data": serializer.data}, status=status.HTTP_200_OK)


class DeleteBookmarkView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def delete(self, request, bookmark_id):
        try:
            # Coba ambil bookmark berdasarkan ID
            bookmark = Bookmark.objects.get(id=bookmark_id, student=request.user)
        except Bookmark.DoesNotExist:
            return Response({"message": "Bookmark not found"}, status=status.HTTP_404_NOT_FOUND)

        # Hapus bookmark
        bookmark.delete()
        return Response({"message": "Bookmark deleted successfully"}, status=status.HTTP_200_OK)


class ShowCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ambil semua kategori
        categories = Category.objects.all()
        
        # Serialisasi data kategori
        serializer = CategorySerializer(categories, many=True)
        
        # Mengembalikan response dengan pesan dan data kategori
        return Response({
            "message": "Get categories success",  # Menambahkan pesan sukses
            "data": serializer.data  # Menambahkan data kategori yang diserialisasi
        }, status=status.HTTP_200_OK)


class DeleteCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        # Pastikan kategori ini belum digunakan di kursus lain
        if category.courses.exists():
            return Response({"message": "Cannot delete category because it is assigned to courses"}, status=status.HTTP_400_BAD_REQUEST)

        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_200_OK)


class EditCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, course_id):
        course_data = request.data
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update course details
        course.name = course_data.get("name", course.name)
        course.description = course_data.get("description", course.description)
        course.price = course_data.get("price", course.price)
        category_id = course_data.get("category")
        if category_id:
            course.category = Category.objects.get(id=category_id)  # Menetapkan kategori baru

        course.save()
        return Response({"message": "Course updated successfully"}, status=status.HTTP_200_OK)

