# lms_core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

from lms_core.models import Course, Profile, CourseMember, CourseAnnouncement, Category, Bookmark, CourseContent

class UserListSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class UserProfileSerializer(serializers.ModelSerializer):
    courses_joined = serializers.SerializerMethodField()
    courses_created = serializers.SerializerMethodField()

    username = serializers.CharField(source='profile.user.username', read_only=True)
    phone_number = serializers.CharField(source='profile.phone_number', allow_null=True, required=False)
    description = serializers.CharField(source='profile.description', allow_null=True, required=False)
    profile_picture = serializers.ImageField(source='profile.profile_picture', allow_null=True, required=False)
    role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'courses_joined', 'courses_created', 
                  'phone_number', 'description', 'profile_picture', 'role']

    def get_courses_joined(self, obj):
        user = obj
        if hasattr(user, 'profile') and user.profile.role == 'teacher':
            return []  # Teacher tidak boleh join kursus
        courses = CourseMember.objects.filter(user_id=user)
        return CourseSerializer([course.course_id for course in courses], many=True).data

    def get_courses_created(self, obj):
        user = obj
        courses = Course.objects.filter(teacher=user)
        return CourseSerializer(courses, many=True).data

    def update(self, instance, validated_data):
        # Di sini, `instance` adalah instance dari Profile
        profile_data = validated_data.pop('profile', {})

        # Update fields dalam Profile langsung
        if 'phone_number' in profile_data:
            instance.phone_number = profile_data['phone_number']
        if 'description' in profile_data:
            instance.description = profile_data['description']
        if 'profile_picture' in profile_data:
            instance.profile_picture = profile_data['profile_picture']

        instance.save()  # Menyimpan perubahan di Profile

        # Update User fields
        instance.user.first_name = validated_data.get('first_name', instance.user.first_name)
        instance.user.last_name = validated_data.get('last_name', instance.user.last_name)
        instance.user.email = validated_data.get('email', instance.user.email)

        instance.user.save()  # Menyimpan perubahan di User

        return instance

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[('teacher', 'Teacher'), ('student', 'Student')])
    phone_number = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name',
                  'role', 'phone_number', 'description', 'profile_picture']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        role = validated_data.pop('role', 'student')
        phone_number = validated_data.pop('phone_number', '')
        description = validated_data.pop('description', '')
        profile_picture = validated_data.pop('profile_picture', None)

        user = User.objects.create_user(**validated_data)

        # Cek apakah Profile sudah ada sebelum membuat baru
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': role,
                'phone_number': phone_number,
                'description': description,
                'profile_picture': profile_picture
            }
        )
        if not created:
            # Jika profile sudah ada, update field-nya
            profile.role = role
            profile.phone_number = phone_number
            profile.description = description
            profile.profile_picture = profile_picture
            profile.save()

        return user

class BatchEnrollSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    student_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def validate(self, data):
        request = self.context['request']
        user = request.user

        # Pastikan course milik teacher yang sedang login
        try:
            course = Course.objects.get(id=data['course_id'], teacher=user)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Kursus tidak ditemukan atau bukan milik Anda.")

        return data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Menyertakan kategori dalam response course

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'price', 'image', 'teacher', 'created_at', 'updated_at', 'category']

class CourseContentSerializer(serializers.ModelSerializer):
    course_id = CourseSerializer()  # Menyertakan detail course dalam konten

    class Meta:
        model = CourseContent
        fields = ['id', 'name', 'description', 'video_url', 'file_attachment', 'course_id', 'parent_id', 'created_at', 'updated_at']

class BookmarkSerializer(serializers.ModelSerializer):
    content = CourseContentSerializer()  # Menyertakan detail konten kursus
    course = serializers.SerializerMethodField()  # Mendapatkan course terkait dari course_content

    class Meta:
        model = Bookmark
        fields = ['id', 'student', 'content', 'course', 'created_at']

    def get_course(self, obj):
        # Mengambil course yang terkait dengan course_content
        return CourseSerializer(obj.content.course_id).data

class CourseAnnouncementSerializer(serializers.ModelSerializer):
    teacher = serializers.StringRelatedField()  # Menampilkan username teacher
    course = CourseSerializer()

    class Meta:
        model = CourseAnnouncement
        fields = ['id', 'course', 'teacher', 'title', 'content', 'created_at', 'updated_at']  # Pastikan ini ada

