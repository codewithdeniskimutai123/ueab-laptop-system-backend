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