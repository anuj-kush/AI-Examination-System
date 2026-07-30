from django.contrib import admin
from django.urls import path,include
from django.views import View
from exam import views


urlpatterns = [
    path('',views.home,name='home'),
    path('base/',views.base,name='base'),
    path('about/', views.about, name='about'),
    path('student-signup/', views.student_signup, name='student-signup'),
    path('student-login/', views.student_login, name='student-login'),
    path('teacher-login/', views.teacher_login, name='teacher-login'),
    path('logout/', views.logout_view, name='logout'),
    path('teacher-dashboard/',views.teacher_dashboard_view,name='teacher-dashboard'),
    path('admin-add-question/',views.admin_add_question_view,name='admin-add-question'),
    path('student-exam/<int:pk>/', views.take_exam, name='student-exam'), 
    path('view-result/',views.view_result_view,name='view-result-view'),
    path('view-students/',views.view_students,name='view-students'),
    path('view-courses/',views.view_courses,name='view-courses'),
    path('admin-view-question/<int:pk>/', views.admin_view_question_view, name='admin-view-question'),
    path('delete-question/<int:pk>/',views.delete_question_view,name='delete-question'),
    path('edit-question/<int:pk>/',views.edit_question,name='edit-question'),
    path('student-dashboard/',views.student_dashboard,name='student-dashboard'),
    path('delete-result/<int:pk>/', views.delete_result_view, name='delete-result'),
    path('about/',views.about,name='about'),
    path('contact/',views.contactus_view,name='contactus'),
    path('download-pdf/<int:pk>', views.download_result_pdf, name='download-pdf'),
    path('calculate-marks/<int:pk>/', views.calculate_marks_view, name='calculate-marks'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('teacher-signup/', views.teacher_signup_view, name='teacher-signup'),

    path('admin-add-course/', views.admin_add_course_view, name='admin-add-course'),
    path('view-result/', views.view_result_view, name='view-result'),
    path('generate-ai-questions/', views.generate_ai_questions_views, name='generate-ai-questions'),
    path('download-certificate/<int:pk>/', views.download_certificate, name='download-certificate'),
    path('edit-course/<int:pk>/', views.edit_course_view, name='edit-course'),
    path('delete-course/<int:pk>/', views.delete_course_view, name='delete-course'),
    path('delete-question/<int:pk>/', views.delete_question_view, name='delete-question'),
    path('upload-pdf-questions/', views.upload_pdf_questions, name='upload-pdf-questions'),
    path('chat-tutor/', views.chat_with_tutor, name='chat-tutor'),
]