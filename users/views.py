from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenSerializer
from .models import User
from .serializers import UserSerializer, StudentProfileSerializer
from .serializers import UpdateProfileSerializer
from django.db.models import Q
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from .models import PasswordResetToken

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_profile(request):

    serializer = StudentProfileSerializer(request.user)

    return Response(serializer.data)

@api_view(['GET'])
def get_users(request):

    users = User.objects.all()
    serializer = UserSerializer(users, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_user(request, pk):

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)

class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    if request.method == "GET":
        serializer = UpdateProfileSerializer(user)
        return Response(serializer.data)
    serializer = UpdateProfileSerializer(
        user,
        data=request.data,
        partial=True,
        context={"request": request}
    )

    if serializer.is_valid():
        serializer.save()

        return Response({
            "message": "Profile updated successfully",
            "data": serializer.data
        })

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_student(request):
    query = request.GET.get("query", "").strip()

    if not query:
        return Response([])

    students = User.objects.filter(
        role="student"
    ).filter(
        Q(student_id__icontains=query) |
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )[:10]

    data = [
        {
            "id": student.id,
            "username": student.username,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "student_id": student.student_id,
            "email": student.email,
        }
        for student in students
    ]

    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "This email address is not registered in the system."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

    token_str = PasswordResetToken.generate_token()
    PasswordResetToken.objects.create(user=user, token=token_str)

    try:
        send_mail(
            subject="UEAB Library - Password Reset Code",
            message=f"Your password reset verification code is: {token_str}. It expires in 15 minutes.",
            from_email="noreply@ueab.ac.ke",
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        return Response({"error": "Failed to send email. Try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "Verification code sent successfully."}, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    email = request.data.get("email")
    token_str = request.data.get("token")
    new_password = request.data.get("new_password")

    if not all([email, token_str, new_password]):
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        token_obj = PasswordResetToken.objects.filter(user=user, token=token_str).latest('created_at')
    except (User.DoesNotExist, PasswordResetToken.DoesNotExist):
        return Response({"error": "Invalid email or verification code"}, status=status.HTTP_400_BAD_REQUEST)

    if not token_obj.is_valid():
        return Response({"error": "This code has expired or already been used"}, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 6:
        return Response({"error": "Password must be at least 6 characters long"}, status=status.HTTP_400_BAD_REQUEST)

    user.password = make_password(new_password)
    user.save()

    token_obj.is_used = True
    token_obj.save()

    return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
