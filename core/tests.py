"""
QuizMaster Pro - Minimal Necessary Test Suite
Run with: python manage.py test core
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import (
    Quiz, Question, Answer, UserSubmission,
    UserAnswer, Event, UserProfile
)

# ============================================================
# MODEL TESTS
# ============================================================


class QuizModelTest(TestCase):
    """Test cases for Quiz model"""

    def setUp(self):
        """Set up test data for Quiz model tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='This is a test quiz description',
            created_by=self.user,
            is_published=True
        )

    def test_quiz_creation(self):
        """Test that a quiz can be created successfully"""
        self.assertEqual(self.quiz.title, 'Test Quiz')
        self.assertEqual(self.quiz.description, 'This is a test quiz description')
        self.assertEqual(self.quiz.created_by, self.user)
        self.assertTrue(self.quiz.is_published)

    def test_quiz_str_representation(self):
        """Test the string representation of Quiz"""
        self.assertEqual(str(self.quiz), 'Test Quiz')

    def test_quiz_get_questions_count(self):
        """Test get_questions_count method returns correct count"""
        # Initially no questions
        self.assertEqual(self.quiz.get_questions_count(), 0)

        # Add questions
        Question.objects.create(quiz=self.quiz, text='Question 1')
        Question.objects.create(quiz=self.quiz, text='Question 2')

        self.assertEqual(self.quiz.get_questions_count(), 2)

    def test_quiz_get_submissions_count(self):
        """Test get_submissions_count method returns correct count"""
        # Initially no submissions
        self.assertEqual(self.quiz.get_submissions_count(), 0)

        # Add submissions
        UserSubmission.objects.create(quiz=self.quiz, user_name='User1', score=2)
        UserSubmission.objects.create(quiz=self.quiz, user_name='User2', score=1)

        self.assertEqual(self.quiz.get_submissions_count(), 2)

    def test_quiz_get_average_score(self):
        """Test get_average_score method calculates correctly"""
        # Create questions first
        Question.objects.create(quiz=self.quiz, text='Q1')
        Question.objects.create(quiz=self.quiz, text='Q2')

        # No submissions - should return 0
        self.assertEqual(self.quiz.get_average_score(), 0)

        # Add submissions with scores
        UserSubmission.objects.create(quiz=self.quiz, user_name='User1', score=2)  # 100%
        UserSubmission.objects.create(quiz=self.quiz, user_name='User2', score=1)  # 50%

        # Average should be 75%
        self.assertEqual(self.quiz.get_average_score(), 75.0)

    def test_quiz_ordering(self):
        """Test that quizzes are ordered by created_at descending"""
        # Verify the model Meta ordering is correct
        self.assertEqual(Quiz._meta.ordering, ['-created_at'])
        
        # Create second quiz with a slight delay to ensure different timestamp
        import time
        time.sleep(0.01)
        quiz2 = Quiz.objects.create(title='Quiz 2', description='Second quiz')
        
        quizzes = list(Quiz.objects.all())
        
        # Most recent should be first
        self.assertEqual(quizzes[0].title, 'Quiz 2')
        self.assertEqual(quizzes[1].title, 'Test Quiz')

class QuestionModelTest(TestCase):
    """Test cases for Question model"""

    def setUp(self):
        """Set up test data for Question model tests"""
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test description'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='What is 2 + 2?',
            question_type='MCQ',
            order=1
        )

    def test_question_creation(self):
        """Test that a question can be created successfully"""
        self.assertEqual(self.question.text, 'What is 2 + 2?')
        self.assertEqual(self.question.quiz, self.quiz)
        self.assertEqual(self.question.question_type, 'MCQ')
        self.assertEqual(self.question.order, 1)

    def test_question_str_representation(self):
        """Test the string representation of Question"""
        expected = f"{self.quiz.title} - What is 2 + 2?"
        self.assertEqual(str(self.question), expected)

    def test_question_get_correct_answer(self):
        """Test get_correct_answer method returns correct answer"""
        # Create answers
        Answer.objects.create(
            question=self.question,
            text='3',
            is_correct=False
        )
        correct_answer = Answer.objects.create(
            question=self.question,
            text='4',
            is_correct=True
        )

        self.assertEqual(self.question.get_correct_answer(), correct_answer)

    def test_question_get_correct_answer_returns_none(self):
        """Test get_correct_answer returns None when no correct answer"""
        Answer.objects.create(
            question=self.question,
            text='3',
            is_correct=False
        )

        self.assertIsNone(self.question.get_correct_answer())

    def test_question_ordering(self):
        """Test that questions are ordered by order field"""
        q2 = Question.objects.create(quiz=self.quiz, text='Q2', order=2)
        q3 = Question.objects.create(quiz=self.quiz, text='Q3', order=0)

        questions = self.quiz.questions.all()
        self.assertEqual(questions[0], q3)         # order=0
        self.assertEqual(questions[1], self.question)  # order=1
        self.assertEqual(questions[2], q2)         # order=2


class AnswerModelTest(TestCase):
    """Test cases for Answer model"""

    def setUp(self):
        """Set up test data for Answer model tests"""
        self.quiz = Quiz.objects.create(title='Test Quiz', description='Test')
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question'
        )
        self.correct_answer = Answer.objects.create(
            question=self.question,
            text='Correct Answer',
            is_correct=True
        )
        self.wrong_answer = Answer.objects.create(
            question=self.question,
            text='Wrong Answer',
            is_correct=False
        )

    def test_answer_creation(self):
        """Test that an answer can be created successfully"""
        self.assertEqual(self.correct_answer.text, 'Correct Answer')
        self.assertTrue(self.correct_answer.is_correct)
        self.assertEqual(self.wrong_answer.text, 'Wrong Answer')
        self.assertFalse(self.wrong_answer.is_correct)

    def test_answer_str_representation(self):
        """Test the string representation of Answer"""
        self.assertEqual(str(self.correct_answer), 'Correct Answer (Correct)')
        self.assertEqual(str(self.wrong_answer), 'Wrong Answer (Incorrect)')

    def test_answer_belongs_to_question(self):
        """Test that answer is linked to correct question"""
        self.assertEqual(self.correct_answer.question, self.question)
        self.assertIn(self.correct_answer, self.question.answers.all())


class UserSubmissionModelTest(TestCase):
    """Test cases for UserSubmission model"""

    def setUp(self):
        """Set up test data for UserSubmission model tests"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test description'
        )
        # Create 4 questions
        for i in range(4):
            Question.objects.create(quiz=self.quiz, text=f'Question {i+1}')

        self.submission = UserSubmission.objects.create(
            quiz=self.quiz,
            user=self.user,
            user_name='testuser',
            score=3
        )

    def test_submission_creation(self):
        """Test that a submission can be created successfully"""
        self.assertEqual(self.submission.quiz, self.quiz)
        self.assertEqual(self.submission.user, self.user)
        self.assertEqual(self.submission.user_name, 'testuser')
        self.assertEqual(self.submission.score, 3)

    def test_submission_str_representation(self):
        """Test the string representation of UserSubmission"""
        expected = 'testuser - Test Quiz - Score: 3'
        self.assertEqual(str(self.submission), expected)

    def test_submission_get_percentage(self):
        """Test get_percentage method calculates correctly"""
        # 3 out of 4 = 75%
        self.assertEqual(self.submission.get_percentage(), 75.0)

    def test_submission_get_percentage_zero_questions(self):
        """Test get_percentage returns 0 when no questions"""
        empty_quiz = Quiz.objects.create(title='Empty', description='No questions')
        submission = UserSubmission.objects.create(
            quiz=empty_quiz,
            user_name='test',
            score=0
        )
        self.assertEqual(submission.get_percentage(), 0)

    def test_submission_get_display_name_authenticated(self):
        """Test get_display_name returns username for authenticated user"""
        self.assertEqual(self.submission.get_display_name(), 'testuser')

    def test_submission_get_display_name_anonymous(self):
        """Test get_display_name returns user_name for anonymous user"""
        anonymous_submission = UserSubmission.objects.create(
            quiz=self.quiz,
            user=None,
            user_name='Anonymous User',
            score=2
        )
        self.assertEqual(anonymous_submission.get_display_name(), 'Anonymous User')

    def test_submission_ordering(self):
        """Test that submissions are ordered by submitted_at descending"""
        # Verify the model Meta ordering is correct
        self.assertEqual(UserSubmission._meta.ordering, ['-submitted_at'])
        
        import time
        time.sleep(0.01)
        submission2 = UserSubmission.objects.create(
            quiz=self.quiz,
            user_name='user2',
            score=4
        )
        submissions = list(UserSubmission.objects.all())

        # Most recent should be first
        self.assertEqual(submissions[0].user_name, 'user2')
        self.assertEqual(submissions[1].user_name, 'testuser')

class UserAnswerModelTest(TestCase):
    """Test cases for UserAnswer model"""

    def setUp(self):
        """Set up test data for UserAnswer model tests"""
        self.quiz = Quiz.objects.create(title='Test Quiz', description='Test')
        self.question = Question.objects.create(quiz=self.quiz, text='Q1')
        self.answer = Answer.objects.create(
            question=self.question,
            text='Answer',
            is_correct=True
        )
        self.submission = UserSubmission.objects.create(
            quiz=self.quiz,
            user_name='test',
            score=1
        )
        self.user_answer = UserAnswer.objects.create(
            submission=self.submission,
            question=self.question,
            answer=self.answer,
            is_correct=True
        )

    def test_user_answer_creation(self):
        """Test that a user answer can be created successfully"""
        self.assertEqual(self.user_answer.submission, self.submission)
        self.assertEqual(self.user_answer.question, self.question)
        self.assertEqual(self.user_answer.answer, self.answer)
        self.assertTrue(self.user_answer.is_correct)

    def test_user_answer_str_representation(self):
        """Test the string representation of UserAnswer"""
        expected = f"test - Q: {self.question.id}"
        self.assertEqual(str(self.user_answer), expected)


class EventModelTest(TestCase):
    """Test cases for Event model"""

    def setUp(self):
        """Set up test data for Event model tests"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.future_date = timezone.now() + timedelta(days=30)
        self.past_date = timezone.now() - timedelta(days=30)

        self.upcoming_event = Event.objects.create(
            title='Upcoming Event',
            description='This event is in the future',
            date=self.future_date,
            location='Test Location',
            created_by=self.user
        )
        self.past_event = Event.objects.create(
            title='Past Event',
            description='This event already happened',
            date=self.past_date,
            location='Old Location',
            created_by=self.user
        )

    def test_event_creation(self):
        """Test that an event can be created successfully"""
        self.assertEqual(self.upcoming_event.title, 'Upcoming Event')
        self.assertEqual(self.upcoming_event.location, 'Test Location')
        self.assertEqual(self.upcoming_event.created_by, self.user)

    def test_event_str_representation(self):
        """Test the string representation of Event"""
        date_str = self.future_date.strftime('%Y-%m-%d')
        expected = f"Upcoming Event - {date_str}"
        self.assertEqual(str(self.upcoming_event), expected)

    def test_event_is_upcoming_true(self):
        """Test is_upcoming returns True for future events"""
        self.assertTrue(self.upcoming_event.is_upcoming())

    def test_event_is_upcoming_false(self):
        """Test is_upcoming returns False for past events"""
        self.assertFalse(self.past_event.is_upcoming())

    def test_event_ordering(self):
        """Test that events are ordered by date ascending"""
        events = Event.objects.all()
        self.assertEqual(events[0], self.past_event)
        self.assertEqual(events[1], self.upcoming_event)


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""

    def setUp(self):
        """Set up test data for UserProfile model tests"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            avatar_color='#FF5733'
        )

    def test_profile_creation(self):
        """Test that a profile can be created successfully"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.avatar_color, '#FF5733')

    def test_profile_str_representation(self):
        """Test the string representation of UserProfile"""
        self.assertEqual(str(self.profile), "testuser's Profile")

    def test_profile_get_total_quizzes_taken(self):
        """Test get_total_quizzes_taken method"""
        self.assertEqual(self.profile.get_total_quizzes_taken(), 0)

        # Create quiz and submission
        quiz = Quiz.objects.create(title='Test', description='Test')
        UserSubmission.objects.create(
            quiz=quiz,
            user=self.user,
            user_name='testuser',
            score=5
        )

        self.assertEqual(self.profile.get_total_quizzes_taken(), 1)

    def test_profile_get_average_score(self):
        """Test get_average_score method"""
        self.assertEqual(self.profile.get_average_score(), 0)

        # Create quiz with questions and submissions
        quiz = Quiz.objects.create(title='Test', description='Test')
        for i in range(10):
            Question.objects.create(quiz=quiz, text=f'Q{i}')

        UserSubmission.objects.create(quiz=quiz, user=self.user, user_name='test', score=8)
        UserSubmission.objects.create(quiz=quiz, user=self.user, user_name='test', score=6)

        # Average: (80% + 60%) / 2 = 70%
        self.assertEqual(self.profile.get_average_score(), 70.0)

    def test_profile_get_quizzes_created(self):
        """Test get_quizzes_created method"""
        self.assertEqual(self.profile.get_quizzes_created(), 0)

        Quiz.objects.create(title='Quiz 1', description='Test', created_by=self.user)
        Quiz.objects.create(title='Quiz 2', description='Test', created_by=self.user)

        self.assertEqual(self.profile.get_quizzes_created(), 2)


# ============================================================
# CORE VIEW TESTS (PUBLIC)
# ============================================================


class PublicViewTests(TestCase):
    """Test cases for public views (no authentication required)"""

    def setUp(self):
        """Set up test data and client"""
        self.client = Client()
        self.quiz = Quiz.objects.create(
            title='Public Quiz',
            description='A quiz for everyone',
            is_published=True
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='Test Question'
        )
        self.answer1 = Answer.objects.create(
            question=self.question,
            text='Correct',
            is_correct=True
        )
        self.answer2 = Answer.objects.create(
            question=self.question,
            text='Wrong',
            is_correct=False
        )
        self.event = Event.objects.create(
            title='Public Event',
            description='An event for everyone',
            date=timezone.now() + timedelta(days=10),
            location='Test Location'
        )

    def test_home_view(self):
        """Test home page loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_quiz_list_view(self):
        """Test quiz list page loads successfully"""
        response = self.client.get(reverse('quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quiz_list.html')
        self.assertContains(response, 'Public Quiz')

    def test_quiz_detail_view(self):
        """Test quiz detail page loads successfully"""
        response = self.client.get(reverse('quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quiz_detail.html')
        self.assertContains(response, 'Public Quiz')

    def test_quiz_detail_view_404(self):
        """Test quiz detail returns 404 for non-existent quiz"""
        response = self.client.get(reverse('quiz_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_quiz_attempt_view_get(self):
        """Test quiz attempt page loads successfully"""
        response = self.client.get(reverse('quiz_attempt', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quiz_attempt.html')

    def test_quiz_attempt_view_post(self):
        """Test quiz submission works correctly"""
        response = self.client.post(reverse('quiz_attempt', args=[self.quiz.id]), {
            'user_name': 'Test User',
            f'question_{self.question.id}': self.answer1.id
        })

        # Should redirect to result page
        self.assertEqual(response.status_code, 302)

        # Check submission was created
        submission = UserSubmission.objects.filter(user_name='Test User').first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.score, 1)

    def test_quiz_result_view(self):
        """Test quiz result page loads successfully"""
        submission = UserSubmission.objects.create(
            quiz=self.quiz,
            user_name='Test User',
            score=1
        )
        response = self.client.get(reverse('quiz_result', args=[submission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quiz_result.html')

    def test_event_list_view(self):
        """Test event list page loads successfully"""
        response = self.client.get(reverse('event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/event_list.html')
        self.assertContains(response, 'Public Event')

    def test_quiz_history_view(self):
        """Test quiz history page loads successfully"""
        response = self.client.get(reverse('quiz_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quiz_history.html')

