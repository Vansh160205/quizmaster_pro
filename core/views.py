"""
QuizMaster Pro - Views
Handles all the business logic for quiz attempts, submissions, events, 
user authentication, and dashboard
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event, UserProfile
from .forms import CustomUserCreationForm, QuizForm, QuestionForm, AnswerFormSet, EventForm


def home(request):
    """
    Home Page View
    Displays featured quizzes and upcoming events on the landing page
    """
    # Get latest 3 quizzes for featured section
    featured_quizzes = Quiz.objects.filter(is_published=True)[:3]
    
    # Get upcoming events (events with date in the future)
    upcoming_events = Event.objects.filter(date__gte=timezone.now())[:3]
    
    # Get recent submissions for leaderboard
    recent_submissions = UserSubmission.objects.all()[:5]
    
    context = {
        'featured_quizzes': featured_quizzes,
        'upcoming_events': upcoming_events,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'core/home.html', context)


def quiz_list(request):
    """
    Quiz List View
    Displays all available quizzes with their details
    """
    quizzes = Quiz.objects.filter(is_published=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        quizzes = quizzes.filter(title__icontains=search_query)
    
    context = {
        'quizzes': quizzes,
        'search_query': search_query,
    }
    return render(request, 'core/quiz_list.html', context)


def quiz_detail(request, quiz_id):
    """
    Quiz Detail View
    Shows quiz information and allows user to start the quiz
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions_count = quiz.questions.count()
    
    context = {
        'quiz': quiz,
        'questions_count': questions_count,
    }
    return render(request, 'core/quiz_detail.html', context)


def quiz_attempt(request, quiz_id):
    """
    Quiz Attempt View
    Dynamically loads all questions and answers for the quiz
    Handles both GET (display quiz) and POST (submit answers)
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related('answers')
    
    if request.method == 'POST':
        # Process quiz submission
        if request.user.is_authenticated:
            user_name = request.user.username
        else:
            user_name = request.POST.get('user_name', 'Anonymous')
        
        # Validate user name
        if not user_name.strip():
            user_name = 'Anonymous'
        
        # Create user submission record
        submission = UserSubmission.objects.create(
            quiz=quiz,
            user=request.user if request.user.is_authenticated else None,
            user_name=user_name,
            score=0
        )
        
        correct_count = 0
        
        # Process each question's answer
        for question in questions:
            # Get the selected answer ID from form
            answer_id = request.POST.get(f'question_{question.id}')
            
            selected_answer = None
            is_correct = False
            
            if answer_id:
                try:
                    # Get the selected answer object
                    selected_answer = Answer.objects.get(id=answer_id)
                    is_correct = selected_answer.is_correct
                    
                    if is_correct:
                        correct_count += 1
                except Answer.DoesNotExist:
                    pass
            
            # Save user's answer for this question
            UserAnswer.objects.create(
                submission=submission,
                question=question,
                answer=selected_answer,
                is_correct=is_correct
            )
        
        # Update the submission with final score
        submission.score = correct_count
        submission.save()
        
        # Redirect to results page
        return redirect('quiz_result', submission_id=submission.id)
    
    # GET request - display the quiz
    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'core/quiz_attempt.html', context)


def quiz_result(request, submission_id):
    """
    Quiz Result View
    Displays the user's score and detailed results after submission
    """
    submission = get_object_or_404(UserSubmission, id=submission_id)
    user_answers = submission.user_answers.all().select_related('question', 'answer')
    
    total_questions = submission.quiz.questions.count()
    percentage = submission.get_percentage()
    
    # Determine result message based on score
    if percentage >= 80:
        result_message = "Excellent! Outstanding performance!"
        result_class = "text-green-600"
    elif percentage >= 60:
        result_message = "Good job! Keep it up!"
        result_class = "text-blue-600"
    elif percentage >= 40:
        result_message = "Not bad! Room for improvement."
        result_class = "text-yellow-600"
    else:
        result_message = "Keep practicing! You'll do better next time."
        result_class = "text-red-600"
    
    context = {
        'submission': submission,
        'user_answers': user_answers,
        'total_questions': total_questions,
        'percentage': percentage,
        'result_message': result_message,
        'result_class': result_class,
    }
    return render(request, 'core/quiz_result.html', context)


def event_list(request):
    """
    Event List View
    Displays all upcoming events with title, date, and location
    """
    # Get all events, upcoming first
    current_time = timezone.now()
    upcoming_events = Event.objects.filter(date__gte=current_time)
    past_events = Event.objects.filter(date__lt=current_time)[:5]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'core/event_list.html', context)


def quiz_history(request):
    """
    Quiz History View (Bonus Feature)
    Shows all past quiz submissions
    """
    submissions = UserSubmission.objects.all().select_related('quiz', 'user')
    
    context = {
        'submissions': submissions,
    }
    return render(request, 'core/quiz_history.html', context)


# ============== Authentication Views ==============

def register_view(request):
    """
    User Registration View
    Allows new users to create an account
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to QuizMaster Pro, {user.username}!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/auth/register.html', context)


def login_view(request):
    """
    User Login View
    Allows existing users to log in
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/auth/login.html', context)


def logout_view(request):
    """
    User Logout View
    Logs out the current user
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


# ============== Dashboard Views ==============

@login_required
def dashboard(request):
    """
    User Dashboard View
    Shows user statistics and quick actions
    """
    user = request.user
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # User's quiz submissions
    my_submissions = UserSubmission.objects.filter(user=user).order_by('-submitted_at')[:5]
    
    # Quizzes created by user
    my_quizzes = Quiz.objects.filter(created_by=user).order_by('-created_at')[:5]
    
    # Events created by user
    my_events = Event.objects.filter(created_by=user).order_by('-date')[:5]
    
    # Statistics
    stats = {
        'total_quizzes_taken': UserSubmission.objects.filter(user=user).count(),
        'average_score': profile.get_average_score(),
        'quizzes_created': Quiz.objects.filter(created_by=user).count(),
        'events_created': Event.objects.filter(created_by=user).count(),
    }
    
    context = {
        'profile': profile,
        'my_submissions': my_submissions,
        'my_quizzes': my_quizzes,
        'my_events': my_events,
        'stats': stats,
    }
    return render(request, 'core/dashboard/dashboard.html', context)


@login_required
def my_quizzes(request):
    """
    View for listing quizzes created by the current user
    """
    quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'quizzes': quizzes,
    }
    return render(request, 'core/dashboard/my_quizzes.html', context)


@login_required
def my_submissions(request):
    """
    View for listing current user's quiz submissions
    """
    submissions = UserSubmission.objects.filter(user=request.user).order_by('-submitted_at')
    
    context = {
        'submissions': submissions,
    }
    return render(request, 'core/dashboard/my_submissions.html', context)


@login_required
def create_quiz(request):
    """
    View for creating a new quiz
    """
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, f'Quiz "{quiz.title}" created successfully!')
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        form = QuizForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/dashboard/create_quiz.html', context)


@login_required
def edit_quiz(request, quiz_id):
    """
    View for editing an existing quiz
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, f'Quiz "{quiz.title}" updated successfully!')
            return redirect('my_quizzes')
    else:
        form = QuizForm(instance=quiz)
    
    context = {
        'form': form,
        'quiz': quiz,
    }
    return render(request, 'core/dashboard/edit_quiz.html', context)


@login_required
def delete_quiz(request, quiz_id):
    """
    View for deleting a quiz
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        title = quiz.title
        quiz.delete()
        messages.success(request, f'Quiz "{title}" deleted successfully!')
        return redirect('my_quizzes')
    
    context = {
        'quiz': quiz,
    }
    return render(request, 'core/dashboard/delete_quiz.html', context)


@login_required
def add_questions(request, quiz_id):
    """
    View for adding questions to a quiz
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    questions = quiz.questions.all().prefetch_related('answers')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.order = quiz.questions.count() + 1
            question.save()
            
            # Save answers
            for i in range(1, 5):
                answer_text = request.POST.get(f'answer_{i}')
                is_correct = request.POST.get('correct_answer') == str(i)
                if answer_text:
                    Answer.objects.create(
                        question=question,
                        text=answer_text,
                        is_correct=is_correct
                    )
            
            messages.success(request, 'Question added successfully!')
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'form': form,
    }
    return render(request, 'core/dashboard/add_questions.html', context)


@login_required
def delete_question(request, question_id):
    """
    View for deleting a question
    """
    question = get_object_or_404(Question, id=question_id, quiz__created_by=request.user)
    quiz_id = question.quiz.id
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('add_questions', quiz_id=quiz_id)
    
    return redirect('add_questions', quiz_id=quiz_id)


@login_required
def create_event(request):
    """
    View for creating a new event
    """
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('my_events')
    else:
        form = EventForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/dashboard/create_event.html', context)


@login_required
def my_events(request):
    """
    View for listing events created by the current user
    """
    events = Event.objects.filter(created_by=request.user).order_by('-date')
    
    context = {
        'events': events,
    }
    return render(request, 'core/dashboard/my_events.html', context)


@login_required
def edit_event(request, event_id):
    """
    View for editing an existing event
    """
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('my_events')
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'core/dashboard/edit_event.html', context)


@login_required
def delete_event(request, event_id):
    """
    View for deleting an event
    """
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted successfully!')
        return redirect('my_events')
    
    context = {
        'event': event,
    }
    return render(request, 'core/dashboard/delete_event.html', context)


@login_required
def profile(request):
    """
    View for user profile
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update profile
        user_profile.bio = request.POST.get('bio', '')
        user_profile.avatar_color = request.POST.get('avatar_color', '#4F46E5')
        user_profile.save()
        
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': user_profile,
    }
    return render(request, 'core/dashboard/profile.html', context)