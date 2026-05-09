
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer, StudentProfileSerializer

#register user
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

# get all users
@api_view(['GET'])
def get_users(request):

    users = User.objects.all()
    serializer = UserSerializer(users, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

#get user
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