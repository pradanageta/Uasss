# from locust import HttpUser, TaskSet, task, between
# import json

# class UserBehavior(TaskSet):
#     def on_start(self):
#         self.login()

#     def login(self):
#         response = self.client.post("/auth/sign-in", json={
#             "username": "LarissaWylie", 
#             "password": "RLS71GOH8GF" 
#         })
#         if response.status_code == 200:
#             self.token = response.json().get("access") 
#         else:
#             print("Login failed:", response.text)

#     @task(1)
#     def get_my_courses(self):
#         headers = {"Authorization": f"Bearer {self.token}"}
#         response = self.client.get("/mycourses", headers=headers)
#         if response.status_code == 200:
#             self.courses = response.json() 
#             # print("My Courses:", self.courses)
#             if self.courses:
#                 self.course_id = self.courses[0]['course_id']['id']
#                 self.get_course_contents(self.course_id)

#     def get_course_contents(self, course_id):
#         headers = {"Authorization": f"Bearer {self.token}"}
#         response = self.client.get(f"/courses/{course_id}/contents", headers=headers)
#         if response.status_code == 200:
#             self.contents = response.json() 
#             # print("Course Contents:", self.contents)
#             if self.contents:
#                 self.content_id = self.contents[0]['id'] 
#                 self.post_comment(self.content_id)

#     def post_comment(self, content_id):
#         headers = {"Authorization": f"Bearer {self.token}"}
#         comment_data = {"comment": "This is a test comment."}
#         response = self.client.post(f"/contents/{content_id}/comments", json=comment_data, headers=headers)
#         if response.status_code == 201:
#             self.comment_id = response.json().get("id")
#             # print("Comment posted:", response.json())
#             self.delete_comment(self.comment_id)

#     def delete_comment(self, comment_id):
#         headers = {"Authorization": f"Bearer {self.token}"}
#         response = self.client.delete(f"/comments/{comment_id}", headers=headers)
#         if response.status_code == 200:
#             print("Comment deleted:", response.json())
#         else:
#             print("Failed to delete comment:", response.text)

# class WebsiteUser(HttpUser):
#     tasks = [UserBehavior]
#     wait_time = between(1, 2) 


from locust import HttpUser, TaskSet, task, between
import json

class UserBehavior(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post("/api/login/", json={
            "username": "LarissaWylie",  # ganti sesuai akunmu
            "password": "RLS71GOH8GF"
        })
        if response.status_code == 200:
            self.token = response.json().get("access")
        else:
            print("Login failed:", response.text)

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task
    def get_profile(self):
        self.client.get("/api/v1/profile/", headers=self._headers())

    @task
    def update_profile(self):
        self.client.put("/api/v1/profile/update/", json={
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+6281234567890",
            "description": "Updated via Locust"
        }, headers=self._headers())

    @task
    def get_courses(self):
        self.client.get("/api/v1/courses/", headers=self._headers())

    @task
    def get_course_contents(self):
        self.client.get("/api/v1/contents/", headers=self._headers())

    @task
    def get_categories(self):
        self.client.get("/api/v1/categories/", headers=self._headers())

    @task
    def get_bookmarks(self):
        self.client.get("/api/v1/bookmarks/", headers=self._headers())

    @task
    def get_users(self):
        self.client.get("/api/users/", headers=self._headers())

    @task
    def batch_enroll(self):
        self.client.post("/api/batch-enroll/", json={
            "course_id": 1,
            "student_ids": [17]  # ganti sesuai ID student valid
        }, headers=self._headers())

    @task
    def get_announcements(self):
        self.client.get("/api/v1/courses/1/announcements/", headers=self._headers())

    @task
    def create_announcement(self):
        self.client.post("/api/v1/courses/1/announcements/create/", json={
            "title": "Test Announcement",
            "content": "Created by Locust",
            "date": "2025-07-01T00:00:00Z"
        }, headers=self._headers())

    @task
    def add_category(self):
        self.client.post("/api/v1/categories/add/", json={
            "name": "Kategori Baru Locust"
        }, headers=self._headers())

    @task
    def add_bookmark(self):
        self.client.post("/api/v1/bookmarks/add/", json={
            "content_id": 1  # ganti sesuai konten valid
        }, headers=self._headers())

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 2)

