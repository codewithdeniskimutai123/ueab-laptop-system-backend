import json
import qrcode
from io import BytesIO

from django.core.files import File
from django.core.mail import EmailMessage
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Laptop
from .serializers import LaptopSerializer

from .permissions import IsAdminOnly
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAdminOnly])
def register_laptop(request):

    serializer = LaptopSerializer(data=request.data)

    if serializer.is_valid():
        laptop = serializer.save()

        # ---------------- QR DATA ----------------
        qr_data = {
            "laptop_id": laptop.id,
            "owner": {
                "name": f"{laptop.owner.first_name} {laptop.owner.last_name}",
                "student_id": getattr(laptop.owner, "student_id", None),
                "email": laptop.owner.email
            },
            "current_holder": {
                "name": f"{laptop.current_holder.first_name} {laptop.current_holder.last_name}",
                "student_id": getattr(laptop.current_holder, "student_id", None),
                "email": laptop.current_holder.email
            },
            "brand": laptop.brand,
            "serial_number": laptop.serial_number
        }

        # ---------------- CREATE QR ----------------
        qr_image = qrcode.make(json.dumps(qr_data))

        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)

        file_name = f"{laptop.serial_number}.png"

        # ---------------- SAVE QR TO MODEL ----------------
        laptop.qr_code.save(file_name, File(buffer), save=True)

        # ---------------- ENSURE FILE IS READY ----------------
        laptop.refresh_from_db()

        # ---------------- READ FILE SAFELY ----------------
        with open(laptop.qr_code.path, "rb") as f:
            qr_file = f.read()

        # ---------------- OWNER EMAIL ----------------
        subject = "Laptop Registration Successful"

        message = f"""
Hello {laptop.owner.first_name},

Your laptop has been successfully registered in the UEAB Laptop Security System.
LAPTOP DETAILS
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

        email.attach(
            file_name,
            qr_file,
            "image/png"
        )

        email.send()

        # ---------------- HOLDER EMAIL ----------------
        if laptop.current_holder and laptop.current_holder.email != laptop.owner.email:

            holder_message = f"""
Hello {laptop.current_holder.first_name},

A laptop has been assigned to you temporarily.
LAPTOP DETAILS
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

            email_holder.attach(
                file_name,
                qr_file,
                "image/png"
            )

            email_holder.send()

        return Response({
            "message": "Laptop registered successfully",
            "data": LaptopSerializer(laptop, context={"request": request}).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_qr(request, laptop_id):

    try:
        laptop = Laptop.objects.get(id=laptop_id)

        user = request.user
        if user != laptop.owner and user != laptop.current_holder:
            return Response(
                {"error": "You are not allowed to access this QR code"},
                status=403
            )

        if not laptop.qr_code:
            raise Http404("QR not found")

        return FileResponse(
            laptop.qr_code.open('rb'),
            as_attachment=True,
            filename=f"{laptop.serial_number}_QR.png"
        )

    except Laptop.DoesNotExist:
        raise Http404("Laptop not found")
    


