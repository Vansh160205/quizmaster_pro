"""
QuizMaster Pro - Admin Configuration
Customized admin interface for managing quizzes, questions, answers, events, and users
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event, UserProfile


class AnswerInline(admin.TabularInline):
    """Inline admin for answers - allows adding answers within question form"""
    model = Answer
    extra = 4
    min_num = 2


class QuestionInline(admin.TabularInline):
    """Inline admin for questions - allows adding questions within quiz form"""
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin configuration for Quiz model"""
    list_display = ['title', 'created_by', 'get_questions_count', 'get_submissions_count', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at', 'created_by']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_published']
    
    fieldsets = (
        ('Quiz Information', {
            'fields': ('title', 'description')
        }),
        ('Settings', {
            'fields': ('created_by', 'is_published')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for Question model"""
    list_display = ['text', 'quiz', 'question_type', 'order', 'created_at']
    list_filter = ['quiz', 'question_type']
    search_fields = ['text']
    inlines = [AnswerInline]
    list_editable = ['order']
    ordering = ['quiz', 'order']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin configuration for Answer model"""
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['text']
    list_editable = ['is_correct']


class UserAnswerInline(admin.TabularInline):
    """Inline admin for user answers within submission"""
    model = UserAnswer
    extra = 0
    readonly_fields = ['question', 'answer', 'is_correct']
    can_delete = False


@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for UserSubmission model"""
    list_display = ['user_name', 'user', 'quiz', 'score', 'get_percentage', 'submitted_at']
    list_filter = ['quiz', 'submitted_at', 'user']
    search_fields = ['user_name', 'user__username']
    readonly_fields = ['submitted_at', 'get_percentage']
    inlines = [UserAnswerInline]
    
    def get_percentage(self, obj):
        return f"{obj.get_percentage()}%"
    get_percentage.short_description = 'Percentage'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """Admin configuration for UserAnswer model"""
    list_display = ['submission', 'question', 'answer', 'is_correct']
    list_filter = ['is_correct', 'submission__quiz']
    readonly_fields = ['submission', 'question', 'answer', 'is_correct']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin configuration for Event model"""
    list_display = ['title', 'date', 'location', 'created_by', 'is_upcoming', 'created_at']
    list_filter = ['date', 'created_by']
    search_fields = ['title', 'location']
    ordering = ['date']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'date', 'location')
        }),
        ('Settings', {
            'fields': ('created_by',)
        }),
    )


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    """Extended User admin with profile inline"""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model"""
    list_display = ['user', 'get_total_quizzes_taken', 'get_average_score', 'get_quizzes_created', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'get_total_quizzes_taken', 'get_average_score', 'get_quizzes_created']


# Customize admin site header
admin.site.site_header = "QuizMaster Pro Administration"
admin.site.site_title = "QuizMaster Pro Admin"
admin.site.index_title = "Welcome to QuizMaster Pro Admin Panel"