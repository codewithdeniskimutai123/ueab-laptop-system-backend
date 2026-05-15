import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from laptops.models import Laptop
from users.models import User
from .models import Transaction
from .serializers import(TransactionSerializer, 
                         LaptopMiniSerializer,
                        StudentTransactionSerializer, 
                            SecurityTransactionSerializer)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def preview_transaction(request):

    user = request.user

    if user.role not in ["admin", "security"]:
        return Response(
            {"error": "Not allowed to preview transactions"},
            status=status.HTTP_403_FORBIDDEN
        )

    laptop_id = request.data.get("laptop_id")
    serial = request.data.get("serial_number")
    username = request.data.get("username")

    laptop = None

    if laptop_id:
        laptop = Laptop.objects.filter(id=laptop_id).first()

    elif serial:
        laptop = Laptop.objects.filter(serial_number=serial).first()

    elif username:
        try:
            student = User.objects.get(username=username)
            laptop = Laptop.objects.filter(current_holder=student).first()
        except User.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

    if not laptop:
        return Response({"error": "Laptop not found"}, status=404)

    serializer = LaptopMiniSerializer(
        laptop,
        context={"request": request}
    )

    return Response(serializer.data)
# CONFIRM TRANSACTION
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_transaction(request):

    user = request.user

    if user.role not in ["admin", "security"]:
        return Response(
            {"error": "Not allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    laptop_id = request.data.get("laptop_id")
    action = request.data.get("action")

    try:
        laptop = Laptop.objects.get(id=laptop_id)
    except Laptop.DoesNotExist:
        return Response({"error": "Laptop not found"}, status=404)

    if action == "IN":

        if laptop.is_inside_library:
            return Response({"error": "Already checked in"}, status=400)

        laptop.is_inside_library = True
        tx_type = "CHECK_IN"

    elif action == "OUT":

        if not laptop.is_inside_library:
            return Response({"error": "Already checked out"}, status=400)

        laptop.is_inside_library = False
        laptop.is_checked_out = True
        tx_type = "CHECK_OUT"

    else:
        return Response({"error": "Invalid action"}, status=400)

    laptop.save()

    transaction = Transaction.objects.create(
        laptop=laptop,
        student=laptop.current_holder,
        previous_holder=laptop.current_holder,
        new_holder=laptop.current_holder,
        scanned_by=user,
        action_type=tx_type,
    )

    return Response(
        TransactionSerializer(
            transaction,
            context={"request": request}
        ).data,
        status=201
    )
# TRANSFER OWNERSHIP
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transfer_laptop(request):

    user = request.user

    laptop_id = request.data.get("laptop_id")
    new_holder_id = request.data.get("new_holder_id")

    try:
        laptop = Laptop.objects.get(id=laptop_id)
    except Laptop.DoesNotExist:
        return Response({"error": "Laptop not found"}, status=404)

    if laptop.owner != user:
        return Response(
            {"error": "Only laptop owner can transfer ownership"},
            status=403
        )

    try:
        new_holder = User.objects.get(id=new_holder_id)
    except User.DoesNotExist:
        return Response({"error": "New holder not found"}, status=404)

    old_holder = laptop.current_holder

    laptop.current_holder = new_holder
    laptop.save()

    transaction = Transaction.objects.create(
        laptop=laptop,
        student=new_holder,
        previous_holder=old_holder,
        new_holder=new_holder,
        scanned_by=user,
        action_type="TRANSFER",
    )

    return Response(
        TransactionSerializer(
            transaction,
            context={"request": request}
        ).data,
        status=201
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_transactions(request):

    transactions = Transaction.objects.filter(
        student=request.user
    ).order_by("-created_at")

    serializer = StudentTransactionSerializer(
        transactions,
        many=True
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recent_transactions(request):

    user = request.user

    if user.role not in ["admin", "security"]:
        return Response({"error": "Not allowed"}, status=403)

    transactions = Transaction.objects.all().order_by("-created_at")[:20]

    serializer = SecurityTransactionSerializer(transactions, many=True)

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def scan_qr(request):

    user = request.user

    if user.role not in ["admin", "security"]:
        return Response(
            {"error": "Not allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    qr_data = request.data.get("qr_data")

    if not qr_data:
        return Response(
            {"error": "QR data required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        data = json.loads(qr_data)

        laptop_id = data.get("laptop_id")
        serial_number = data.get("serial_number")

        if not laptop_id or not serial_number:
            return Response(
                {"error": "Invalid QR structure"},
                status=status.HTTP_400_BAD_REQUEST
            )

        laptop = Laptop.objects.select_related("owner", "current_holder").get(
            id=laptop_id,
            serial_number=serial_number
        )

    except Laptop.DoesNotExist:
        return Response(
            {"error": "Laptop not found or QR mismatch"},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception:
        return Response(
            {"error": "Invalid QR code"},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({
        "laptop": {
            "id": laptop.id,
            "brand": laptop.brand,
            "serial_number": laptop.serial_number,
            "is_inside_library": laptop.is_inside_library,
        },

        "owner": {
            "id": laptop.owner.id,
            "name": f"{laptop.owner.first_name} {laptop.owner.last_name}",
            "student_id": getattr(laptop.owner, "student_id", None),
        },

        "current_holder": (
            {
                "id": laptop.current_holder.id,
                "name": f"{laptop.current_holder.first_name} {laptop.current_holder.last_name}",
                "student_id": getattr(laptop.current_holder, "student_id", None),
            }
            if laptop.current_holder else None
        )
    }, status=status.HTTP_200_OK)