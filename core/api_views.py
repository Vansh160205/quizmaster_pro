"""
QuizMaster Pro - API Views
Django REST Framework views for API endpoints
"""

from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404

from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event, UserProfile
from .serializers import (
    QuizListSerializer, QuizDetailSerializer, QuizCreateSerializer,
    QuestionSerializer, QuestionCreateSerializer,
    AnswerSerializer, AnswerDetailSerializer,
    UserSubmissionSerializer, QuizSubmitSerializer,
    EventSerializer, UserSerializer, UserRegistrationSerializer,
    UserProfileSerializer, DashboardStatsSerializer
)


# ============== Quiz API Views ==============

class QuizListAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing all quizzes and creating new ones
    GET: List all published quizzes
    POST: Create a new quiz (authenticated users only)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizCreateSerializer
        return QuizListSerializer

    def get_queryset(self):
        queryset = Quiz.objects.filter(is_published=True)
        
        # Filter by search query
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset


class QuizDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a quiz
    GET: Retrieve quiz details with questions
    PUT/PATCH: Update quiz (owner only)
    DELETE: Delete quiz (owner only)
    """
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QuizCreateSerializer
        return QuizDetailSerializer

    def update(self, request, *args, **kwargs):
        quiz = self.get_object()
        if quiz.created_by != request.user and not request.user.is_staff:
            return Response(
                {"error": "You don't have permission to edit this quiz"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        quiz = self.get_object()
        if quiz.created_by != request.user and not request.user.is_staff:
            return Response(
                {"error": "You don't have permission to delete this quiz"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class QuizSubmitAPIView(APIView):
    """
    API endpoint for submitting quiz answers
    POST: Submit answers and get results
    """
    permission_classes = [AllowAny]

    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        
        serializer = QuizSubmitSerializer(
            data=request.data,
            context={'quiz_id': pk}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        answers_data = serializer.validated_data['answers']
        user_name = request.data.get('user_name', 'Anonymous')

        # Create submission
        submission = UserSubmission.objects.create(
            quiz=quiz,
            user=request.user if request.user.is_authenticated else None,
            user_name=request.user.username if request.user.is_authenticated else user_name,
            score=0
        )

        correct_count = 0

        # Process each answer
        for question_id, answer_id in answers_data.items():
            question = get_object_or_404(Question, pk=int(question_id))
            answer = get_object_or_404(Answer, pk=answer_id)
            is_correct = answer.is_correct

            if is_correct:
                correct_count += 1

            UserAnswer.objects.create(
                submission=submission,
                question=question,
                answer=answer,
                is_correct=is_correct
            )

        # Update score
        submission.score = correct_count
        submission.save()

        # Return result
        result_serializer = UserSubmissionSerializer(submission)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


# ============== Question API Views ==============

class QuestionListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating questions
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionCreateSerializer
        return QuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        if quiz_id:
            return Question.objects.filter(quiz_id=quiz_id)
        return Question.objects.all()


class QuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for question details
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ============== Event API Views ==============

class EventListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating events
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Event.objects.all()
        upcoming_only = self.request.query_params.get('upcoming', None)
        if upcoming_only:
            from django.utils import timezone
            queryset = queryset.filter(date__gte=timezone.now())
        return queryset


class EventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for event details
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ============== User & Auth API Views ==============

class UserRegistrationAPIView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserSubmissionsAPIView(generics.ListAPIView):
    """
    API endpoint for user's quiz submissions
    """
    serializer_class = UserSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSubmission.objects.filter(user=self.request.user)


# ============== Dashboard API Views ==============

class DashboardStatsAPIView(APIView):
    """
    API endpoint for dashboard statistics
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Avg

        # Get statistics
        stats = {
            'total_quizzes': Quiz.objects.count(),
            'total_questions': Question.objects.count(),
            'total_submissions': UserSubmission.objects.count(),
            'total_events': Event.objects.count(),
            'total_users': User.objects.count(),
        }

        # Recent submissions
        recent_submissions = UserSubmission.objects.all()[:5]
        stats['recent_submissions'] = UserSubmissionSerializer(recent_submissions, many=True).data

        # Popular quizzes (by submission count)
        popular_quizzes = Quiz.objects.annotate(
            submission_count=Count('submissions')
        ).order_by('-submission_count')[:5]
        stats['popular_quizzes'] = QuizListSerializer(popular_quizzes, many=True).data

        return Response(stats)


class MyQuizzesAPIView(generics.ListAPIView):
    """
    API endpoint for quizzes created by the authenticated user
    """
    serializer_class = QuizListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(created_by=self.request.user)
    
