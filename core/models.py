"""
QuizMaster Pro - Database Models
Defines all database tables for quizzes, questions, answers, events, and user submissions
Updated with user authentication support
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Quiz(models.Model):
    """
    Quiz Model - Represents a quiz with multiple questions
    Fields: id (auto), title, description, created_by, is_published, created_at, updated_at
    """
    title = models.CharField(max_length=200, help_text="Title of the quiz")
    description = models.TextField(help_text="Detailed description of the quiz")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_quizzes',
        null=True,
        blank=True,
        help_text="User who created this quiz"
    )
    is_published = models.BooleanField(
        default=True, 
        help_text="Only published quizzes are visible to users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_questions_count(self):
        """Returns the total number of questions in this quiz"""
        return self.questions.count()
    
    def get_submissions_count(self):
        """Returns the total number of submissions for this quiz"""
        return self.submissions.count()
    
    def get_average_score(self):
        """Returns the average score percentage for this quiz"""
        submissions = self.submissions.all()
        if not submissions:
            return 0
        total_percentage = sum([s.get_percentage() for s in submissions])
        return round(total_percentage / submissions.count(), 1)


class Question(models.Model):
    """
    Question Model - Represents a question belonging to a quiz
    Fields: id (auto), quiz (FK), text, question_type, order, created_at
    """
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
    ]
    
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name='questions',
        help_text="The quiz this question belongs to"
    )
    text = models.TextField(help_text="The question text")
    question_type = models.CharField(
        max_length=10, 
        choices=QUESTION_TYPES, 
        default='MCQ'
    )
    order = models.PositiveIntegerField(default=0, help_text="Question order in quiz")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"

    def get_correct_answer(self):
        """Returns the correct answer for this question"""
        return self.answers.filter(is_correct=True).first()


class Answer(models.Model):
    """
    Answer Model - Represents an answer option for a question
    Fields: id (auto), question (FK), text, is_correct
    """
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers',
        help_text="The question this answer belongs to"
    )
    text = models.CharField(max_length=500, help_text="The answer text")
    is_correct = models.BooleanField(
        default=False, 
        help_text="Mark if this is the correct answer"
    )

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class UserSubmission(models.Model):
    """
    UserSubmission Model - Records a user's quiz attempt
    Fields: id (auto), quiz (FK), user (FK), user_name, score, submitted_at
    Updated to support authenticated users
    """
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_submissions',
        null=True,
        blank=True,
        help_text="Authenticated user who took the quiz"
    )
    user_name = models.CharField(
        max_length=100, 
        help_text="Name of the user (for anonymous users)"
    )
    score = models.IntegerField(default=0, help_text="Score achieved")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user_name} - {self.quiz.title} - Score: {self.score}"

    def get_percentage(self):
        """Calculate and return the percentage score"""
        total_questions = self.quiz.questions.count()
        if total_questions > 0:
            return round((self.score / total_questions) * 100, 1)
        return 0
    
    def get_display_name(self):
        """Returns the display name (username if authenticated, else user_name)"""
        if self.user:
            return self.user.username
        return self.user_name


class UserAnswer(models.Model):
    """
    UserAnswer Model - Records individual answer selections
    Fields: submission (FK), question (FK), answer (FK), is_correct
    """
    submission = models.ForeignKey(
        UserSubmission, 
        on_delete=models.CASCADE, 
        related_name='user_answers'
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE
    )
    answer = models.ForeignKey(
        Answer, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.submission.user_name} - Q: {self.question.id}"


class Event(models.Model):
    """
    Event Model - Represents an upcoming event
    Fields: id (auto), title, description, date, location, created_by
    """
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(help_text="Event description")
    date = models.DateTimeField(help_text="Event date and time")
    location = models.CharField(max_length=300, help_text="Event location")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events',
        null=True,
        blank=True,
        help_text="User who created this event"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"

    def is_upcoming(self):
        """Check if the event is in the future"""
        return self.date > timezone.now()


class UserProfile(models.Model):
    """
    UserProfile Model - Extended user information
    Links to Django's built-in User model
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, null=True, help_text="User biography")
    avatar_color = models.CharField(
        max_length=7, 
        default='#4F46E5',
        help_text="Hex color for avatar background"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_total_quizzes_taken(self):
        """Returns total number of quizzes taken by user"""
        return self.user.quiz_submissions.count()

    def get_average_score(self):
        """Returns average score across all quizzes"""
        submissions = self.user.quiz_submissions.all()
        if not submissions:
            return 0
        total = sum([s.get_percentage() for s in submissions])
        return round(total / submissions.count(), 1)

    def get_quizzes_created(self):
        """Returns number of quizzes created by user"""
        return self.user.created_quizzes.count()