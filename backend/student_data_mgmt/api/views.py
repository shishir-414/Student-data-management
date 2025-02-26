from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from .serializers import UserSerializer, UserCreateSerializer, StudentSerializer, StudentMarksSerializer
from .models import Student, StudentMarks, User
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        #return currently authenticated user
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
        
        
#View for registering a new user
class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User created successfully",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#view for login
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                "error": "Please provide both username and password"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(username=username).first()
        
        if user and check_password(password, user.password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
            
        return Response({
            "error": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

#view to logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "Logged out",
                "error": str(e)
            }, status=status.HTTP_200_OK)

#view to create and list student
class StudentCreate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        query = request.query_params.get('search', '')
        students = Student.objects.filter(name__icontains=query)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

#view to get, update and delete student
class StudentDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]

    def get(self, request, id):
        student = get_object_or_404(Student, id=id)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, id):
        student = get_object_or_404(Student, id=id)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        student = get_object_or_404(Student, id=id)
        student.delete()
        return Response({"message": "Student deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

#view to get, create, upadte and delete student marks
class StudentsMarks(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]

    def get(self, request, id=None):
        if id:
            student_marks = StudentMarks.objects.filter(student_id=id)
            if not student_marks.exists():
                return Response({"message": "Student marks not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            student_marks = StudentMarks.objects.all()
        serializer = StudentMarksSerializer(student_marks, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create new student marks
        serializer = StudentMarksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Return the created marks with student details
            created_marks = StudentMarks.objects.get(id=serializer.data['id'])
            response_serializer = StudentMarksSerializer(created_marks)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            marks = StudentMarks.objects.get(student_id=id)
            serializer = StudentMarksSerializer(marks, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentMarks.DoesNotExist:
            return Response({"error": "Marks not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            marks = StudentMarks.objects.get(student_id=id)
            marks.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except StudentMarks.DoesNotExist:
            return Response({"error": "Marks not found"}, status=status.HTTP_404_NOT_FOUND)