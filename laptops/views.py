from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Laptop
from .serializers import  MyLaptopSerializer
from django.http import Http404, FileResponse
from django.db.models import Q
#
@api_view(['GET', 'OPTIONS']) 
@permission_classes([IsAuthenticated])
def download_qr(request, laptop_id):
    if request.method == 'OPTIONS':
        return Response(status=200)

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
        response = FileResponse(
            laptop.qr_code.open('rb'),
            as_attachment=True,
            filename=f"{laptop.serial_number}_QR.png"
        )
        return response

    except Laptop.DoesNotExist:
        raise Http404("Laptop not found")

    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_laptop(request):

    user = request.user

    laptop = Laptop.objects.filter(
        Q(current_holder=user) |
        Q(owner=user)
    ).first()

    if not laptop:
        return Response({"message": "No laptop assigned"}, status=404)

    serializer = MyLaptopSerializer(
        laptop,
        context={"request": request}
    )

    return Response(serializer.data)