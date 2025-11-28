"""
QuizMaster Pro - URL Configuration for Core App
Maps URLs to their corresponding views including auth and dashboard
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# API Router
router = DefaultRouter()

urlpatterns = [
    # ============== Public Pages ==============
    # Home page
    path('', views.home, name='home'),
    
    # Quiz URLs
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/attempt/', views.quiz_attempt, name='quiz_attempt'),
    path('result/<int:submission_id>/', views.quiz_result, name='quiz_result'),
    path('history/', views.quiz_history, name='quiz_history'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    
    # ============== Authentication URLs ==============
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ============== Dashboard URLs ==============
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.profile, name='profile'),
    path('dashboard/my-quizzes/', views.my_quizzes, name='my_quizzes'),
    path('dashboard/my-submissions/', views.my_submissions, name='my_submissions'),
    path('dashboard/my-events/', views.my_events, name='my_events'),
    
    # Quiz Management
    path('dashboard/quiz/create/', views.create_quiz, name='create_quiz'),
    path('dashboard/quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('dashboard/quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('dashboard/quiz/<int:quiz_id>/questions/', views.add_questions, name='add_questions'),
    path('dashboard/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    
    # Event Management
    path('dashboard/event/create/', views.create_event, name='create_event'),
    path('dashboard/event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('dashboard/event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    
    # ============== API URLs ==============
    path('api/quizzes/', api_views.QuizListAPIView.as_view(), name='api_quiz_list'),
    path('api/quizzes/<int:pk>/', api_views.QuizDetailAPIView.as_view(), name='api_quiz_detail'),
    path('api/quizzes/<int:pk>/submit/', api_views.QuizSubmitAPIView.as_view(), name='api_quiz_submit'),
    path('api/quizzes/<int:quiz_id>/questions/', api_views.QuestionListCreateAPIView.as_view(), name='api_question_list'),
    path('api/questions/<int:pk>/', api_views.QuestionDetailAPIView.as_view(), name='api_question_detail'),
    path('api/events/', api_views.EventListCreateAPIView.as_view(), name='api_event_list'),
    path('api/events/<int:pk>/', api_views.EventDetailAPIView.as_view(), name='api_event_detail'),
    path('api/register/', api_views.UserRegistrationAPIView.as_view(), name='api_register'),
    path('api/profile/', api_views.UserProfileAPIView.as_view(), name='api_profile'),
    path('api/my-submissions/', api_views.UserSubmissionsAPIView.as_view(), name='api_my_submissions'),
    path('api/my-quizzes/', api_views.MyQuizzesAPIView.as_view(), name='api_my_quizzes'),
    path('api/dashboard-stats/', api_views.DashboardStatsAPIView.as_view(), name='api_dashboard_stats'),
    
    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]