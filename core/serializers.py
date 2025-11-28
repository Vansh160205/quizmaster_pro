"""
QuizMaster Pro - API Serializers
Django REST Framework serializers for converting model instances to JSON
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        """Validate that passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Create user profile
        UserProfile.objects.create(user=user)
        return user


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model"""
    
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']
        extra_kwargs = {
            'is_correct': {'write_only': True}  # Hide correct answer in list view
        }


class AnswerDetailSerializer(serializers.ModelSerializer):
    """Serializer for Answer model with all details (for admin/results)"""
    
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'answers', 'created_at']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating questions with answers"""
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'question_type', 'order', 'answers']

    def create(self, validated_data):
        """Create question with nested answers"""
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for Quiz list view"""
    questions_count = serializers.SerializerMethodField()
    created_by_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions_count', 'created_by_username', 
                  'is_published', 'created_at', 'updated_at']

    def get_questions_count(self, obj):
        return obj.get_questions_count()

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else 'System'


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for Quiz detail view with questions"""
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    submissions_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions', 'created_by',
                  'submissions_count', 'average_score', 'is_published', 
                  'created_at', 'updated_at']

    def get_submissions_count(self, obj):
        return obj.get_submissions_count()

    def get_average_score(self, obj):
        return obj.get_average_score()


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating quizzes"""
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'is_published']

    def create(self, validated_data):
        """Create quiz with current user as creator"""
        user = self.context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)


class UserAnswerSerializer(serializers.ModelSerializer):
    """Serializer for UserAnswer model"""
    question_text = serializers.CharField(source='question.text', read_only=True)
    answer_text = serializers.CharField(source='answer.text', read_only=True)
    correct_answer = serializers.SerializerMethodField()

    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'question_text', 'answer', 'answer_text', 
                  'is_correct', 'correct_answer']

    def get_correct_answer(self, obj):
        correct = obj.question.get_correct_answer()
        return correct.text if correct else None


class UserSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for UserSubmission model"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    percentage = serializers.SerializerMethodField()
    user_answers = UserAnswerSerializer(many=True, read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = UserSubmission
        fields = ['id', 'quiz', 'quiz_title', 'user', 'user_name', 'display_name',
                  'score', 'percentage', 'user_answers', 'submitted_at']

    def get_percentage(self, obj):
        return obj.get_percentage()

    def get_display_name(self, obj):
        return obj.get_display_name()


class QuizSubmitSerializer(serializers.Serializer):
    """Serializer for quiz submission"""
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Dictionary of question_id: answer_id"
    )

    def validate_answers(self, value):
        """Validate that all questions are answered"""
        quiz_id = self.context.get('quiz_id')
        quiz = Quiz.objects.get(id=quiz_id)
        question_ids = set(quiz.questions.values_list('id', flat=True))
        answered_ids = set(int(k) for k in value.keys())
        
        if question_ids != answered_ids:
            missing = question_ids - answered_ids
            raise serializers.ValidationError(
                f"Missing answers for questions: {missing}"
            )
        return value


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    is_upcoming = serializers.SerializerMethodField()
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 
                  'is_upcoming', 'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['created_by']

    def get_is_upcoming(self, obj):
        return obj.is_upcoming()

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else 'System'

    def create(self, validated_data):
        """Create event with current user as creator"""
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['created_by'] = user
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    total_quizzes_taken = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    quizzes_created = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar_color', 'total_quizzes_taken',
                  'average_score', 'quizzes_created', 'created_at']

    def get_total_quizzes_taken(self, obj):
        return obj.get_total_quizzes_taken()

    def get_average_score(self, obj):
        return obj.get_average_score()

    def get_quizzes_created(self, obj):
        return obj.get_quizzes_created()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_quizzes = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    total_submissions = serializers.IntegerField()
    total_events = serializers.IntegerField()
    total_users = serializers.IntegerField()
    recent_submissions = UserSubmissionSerializer(many=True)
    popular_quizzes = QuizListSerializer(many=True)