import json
import qrcode
from io import BytesIO
from datetime import timedelta
from .serializers import LaptopsSerializer
from django.core.files import File
from django.core.mail import EmailMessage
from django.utils import timezone
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from laptops.models import Laptop
from laptops.serializers import LaptopSerializer
from users.models import User
from transactions.models import Transaction
from django.core.mail import EmailMessage
from .permissions import IsAdminOnly
import logging
import os
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAdminOnly])
def register_laptop(request):
    if request.user.role != "admin":
        return Response(
            {"error": "Access Denied: Only system administrators are authorized to register computing hardware assets."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = LaptopSerializer(data=request.data)

    if serializer.is_valid():
        laptop = serializer.save()

        qr_data = {
            "laptop_id": laptop.id,
            "serial_number": laptop.serial_number
        }

        qr_image = qrcode.make(json.dumps(qr_data))

        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)

        file_name = f"{laptop.serial_number}.png"

        laptop.qr_code.save(file_name, File(buffer), save=True)
        laptop.refresh_from_db()

        try:
            with open(laptop.qr_code.path, "rb") as f:
                qr_file = f.read()

            subject = "Laptop Registration Successful"

            message = f"""
Hello {laptop.owner.first_name},

Your laptop has been successfully registered in the UEAB Laptop Security System.

LAPTOP DETAILS:
Brand: {laptop.brand}
Serial Number: {laptop.serial_number}

Download QR:
http://127.0.0.1:8000/api/laptops/download_qr/{laptop.id}/
"""

            email = EmailMessage(
                subject,
                message,
                to=[laptop.owner.email]
            )
            email.attach(file_name, qr_file, "image/png")
            email.send(fail_silently=False)

            if laptop.current_holder and laptop.current_holder.email != laptop.owner.email:
                holder_message = f"""
Hello {laptop.current_holder.first_name},

A laptop has been assigned to you temporarily.

LAPTOP DETAILS:
Brand: {laptop.brand}
Serial Number: {laptop.serial_number}

Download QR:
http://127.0.0.1:8000/api/laptops/download_qr/{laptop.id}/
"""
                email_holder = EmailMessage(
                    subject,
                    holder_message,
                    to=[laptop.current_holder.email]
                )
                email_holder.attach(file_name, qr_file, "image/png")
                email_holder.send(fail_silently=False)

        except Exception as mail_err:
            logger.error(f"CRITICAL SMTP TELEMETRY FAULT: {str(mail_err)}")

        return Response({
            "message": "Laptop registered successfully",
            "data": LaptopSerializer(laptop, context={"request": request}).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_modify_user_role(request):
   
    if request.user.role != "admin":
        return Response({"error": "Access Denied."}, status=status.HTTP_403_FORBIDDEN)

    target_user_id = request.data.get("user_id")
    new_role = request.data.get("role")

    if new_role not in ["student", "security", "admin"]:
        return Response({"error": "Invalid role type specified."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = User.objects.get(id=target_user_id)
        
        if target_user == request.user and new_role != "admin":
            return Response({"error": "System Protocol: You cannot "
            "demote your own account."}, status=status.HTTP_400_BAD_REQUEST)
            
        target_user.role = new_role
        target_user.save()

        return Response({
            "success": f"Account {target_user.username} role updated to: {new_role}."
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "Target student profile record not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_global_analytics(request):
    
    if request.user.role != "admin":
        return Response({"error": "Access Denied."}, status=status.HTTP_403_FORBIDDEN)

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    year_start = today_start - timedelta(days=365)

    laptop_stats = {
        "total": Laptop.objects.count(),
        "active_today": Transaction.objects.filter(created_at__gte=today_start).values('laptop').distinct().count(),
        "active_week": Transaction.objects.filter(created_at__gte=week_start).values('laptop').distinct().count(),
        "active_month": Transaction.objects.filter(created_at__gte=month_start).values('laptop').distinct().count(),
        "active_year": Transaction.objects.filter(created_at__gte=year_start).values('laptop').distinct().count(),
        "by_brand": list(Laptop.objects.values('brand').annotate(count=Count('id')))
    }

    user_stats = {
        "total": User.objects.count(),
        "admins": User.objects.filter(role="admin").count(),
        "security": User.objects.filter(role="security").count(),
        "students": User.objects.filter(role="student").count(),
    }

    transaction_stats = {
        "total": Transaction.objects.count(),
        "check_ins": Transaction.objects.filter(action_type="CHECK_IN").count(),
        "check_outs": Transaction.objects.filter(action_type="CHECK_OUT").count(),
        "transfers": Transaction.objects.filter(action_type="TRANSFER").count(),
    }

    return Response({
        "laptops": laptop_stats,
        "users": user_stats,
        "transactions": transaction_stats
    }, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAdminOnly])
def admin_delete_laptop(request, laptop_id):
    try:
        laptop = Laptop.objects.get(id=laptop_id)
        serial_tracker = laptop.serial_number
        
        laptop.delete()
        
        return Response({
            "success": f"Hardware entry with Serial Number '{serial_tracker}' removed from database registry successfully."
        }, status=status.HTTP_200_OK)
        
    except Laptop.DoesNotExist:
        return Response({"error": "Target laptop record does not exist in the MySQL inventory."}, status=status.HTTP_404_NOT_FOUND)

@api_view(["DELETE"])
@permission_classes([IsAdminOnly])
def admin_delete_user(request, user_id):
    try:
        target_user = User.objects.get(id=user_id)
        
        if target_user == request.user:
            return Response({
                "error": "System Security Breach: Root protection protocol blocks self-deletion."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        username_tracker = target_user.username
        target_user.delete()
        
        return Response({
            "success": f"Account user profile for '{username_tracker}' wiped successfully."
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({"error": "Target user profile row record could not be found."}, 
                        status=status.HTTP_404_NOT_FOUND) # <-- Fixed truncation here

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_laptops(request):
    if request.user.role != "admin":
        return Response(
            {"error": "Access Denied: Only system administrators are authorized to audit the hardware register."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    laptops = Laptop.objects.all().order_by('-id')
    serializer = LaptopSerializer(laptops, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_laptops(request):
    if request.user.role != "admin":
        return Response(
            {"error": "Access Denied: Only system administrators are authorized to audit the hardware register."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    laptops = Laptop.objects.all().order_by('-id')
    serializer = LaptopsSerializer(laptops, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_student(request):
   
    if getattr(request.user, "role", "").lower() != "admin":
        return Response(
            {"error": "Access denied. Admin privileges required."}, 
            status=status.HTTP_403_FORBIDDEN
        )
        
    username = request.query_params.get("username", "").strip()
    if not username:
        return Response(
            {"error": "Please provide a target username query parameter."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        target_user = User.objects.get(username__iexact=username)
        
        photo_url = None
        if getattr(target_user, "profile_photo", None) and target_user.profile_photo:
            photo_url = request.build_absolute_uri(target_user.profile_photo.url)
        
        return Response({
            "id": target_user.id,
            "username": target_user.username,
            "name": f"{target_user.first_name} {target_user.last_name}".strip() or target_user.username,
            "student_id": getattr(target_user, "student_id", "N/A"),
            "email": target_user.email,
            "profile_photo": photo_url
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {"error": "No student record matches that username in the Baraton registry."}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile(request):
    
    if getattr(request.user, "role", "").lower() != "admin":
        return Response(
            {"error": "Access denied. Admin privileges required."}, 
            status=status.HTTP_403_FORBIDDEN
        )
        
    user_id = request.data.get("user_id")
    photo_file = request.FILES.get("profile_photo")
    
    if not user_id:
        return Response(
            {"error": "Target user identifier 'user_id' field is required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if not photo_file:
        return Response(
            {"error": "Profile photo image attachment is required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        target_user = User.objects.get(id=user_id)
        
        if target_user.profile_photo and os.path.exists(target_user.profile_photo.path):
            try:
                os.remove(target_user.profile_photo.path)
            except Exception:
                pass
                
        target_user.profile_photo = photo_file
        target_user.save()
        
        photo_url = request.build_absolute_uri(target_user.profile_photo.url)
        
        return Response({
            "message": "User validation profile picture assigned successfully.",
            "profile_photo": photo_url
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {"error": "Target user registry context is invalid or missing."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred while saving the profile image asset: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
