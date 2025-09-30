from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Task, ProfileImage
from .serializers import TaskSerializer, UserSerializer, UserRegistrationSerializer, LoginSerializer, ProfileImageSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this task.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to delete this task.")
        instance.delete()

class UserRegistrationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)
    
class LoginViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        logout(request)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


class ProfileImageViewSet(viewsets.ModelViewSet):
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
       data = request.data.copy()
       student_id = data.get('student')
       image_file = request.FILES.get('image')

       if not student_id or not image_file:
              return Response({"status": "error", "errors": "Student ID and image file are required."}, status=status.HTTP_400_BAD_REQUEST)
       
       # Upload image to Cloudinary
       try:
            upload_result = cloudinary.uploader.upload(image_file, folder="profile_images/")
            image_url = upload_result.get('secure_url')
            # save in database
            profile = ProfileImage.objects.create(student_id=student_id, image_url=image_url)
            serializer = self.get_serializer(profile)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
       except Exception as e:
            return Response({"status": "error", "errors": f"Image upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
       
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        image_file = request.FILES.get("image")

        if image_file:
            # Optional: delete old image from Cloudinary before uploading new
            if profile.image_url:
                public_id = profile.image_url.split("/")[-1].split(".")[0]  # extract public_id
                cloudinary.uploader.destroy(public_id)

            upload_result = cloudinary.uploader.upload(image_file)
            profile.image = image_file
            profile.image_url = upload_result.get("secure_url")
            profile.save()

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()

        # Delete from Cloudinary if exists
        if profile.image_url:
            try:
                public_id = profile.image_url.split("/")[-1].split(".")[0]
                cloudinary.uploader.destroy(public_id)
            except Exception as e:
                return Response({"error": f"Failed to delete Cloudinary image: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        profile.delete()
        return Response({"message": "Profile and image deleted successfully"},
                        status=status.HTTP_204_NO_CONTENT)