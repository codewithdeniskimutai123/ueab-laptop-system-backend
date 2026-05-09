from django.utils.timezone import now

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from laptops.models import Laptop
from users.models import User
from transactions.models import Transaction
from django.db.models import Q
from .serializers import (
    AdminOverviewSerializer,
    AdminLaptopSerializer,
    AdminUserSerializer,
    AdminTransactionSerializer,
)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_overview(request):

    user = request.user

    # ONLY ADMIN
    if user.role != "admin":
        return Response(
            {"error": "Only admin allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    total_laptops = Laptop.objects.count()
    laptops_inside = Laptop.objects.filter(is_inside_library=True).count()
    laptops_outside = Laptop.objects.filter(is_inside_library=False).count()

    total_students = User.objects.filter(role="student").count()
    total_security = User.objects.filter(role="security").count()
    total_admins = User.objects.filter(role="admin").count()

    total_transactions = Transaction.objects.count()
    today_transactions = Transaction.objects.filter(
        created_at__date=now().date()
    ).count()

    data = {
        "total_laptops": total_laptops,
        "laptops_inside": laptops_inside,
        "laptops_outside": laptops_outside,

        "total_students": total_students,
        "total_security": total_security,
        "total_admins": total_admins,

        "total_transactions": total_transactions,
        "today_transactions": today_transactions,
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_laptops(request):

    user = request.user
    # ONLY ADMIN
    if user.role != "admin":
        return Response(
            {"error": "Only admin allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    search = request.GET.get("search")

    laptops = Laptop.objects.select_related(
        "owner",
        "current_holder"
    ).all()
    # SEARCH
    if search:
        laptops = laptops.filter(

            Q(serial_number__icontains=search)

            |

            Q(owner__student_id__icontains=search)

            |

            Q(current_holder__student_id__icontains=search)

            |

            Q(owner__first_name__icontains=search)

            |

            Q(owner__last_name__icontains=search)

            |

            Q(current_holder__first_name__icontains=search)

            |

            Q(current_holder__last_name__icontains=search)
        )

    serializer = AdminLaptopSerializer(
        laptops,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_laptop_detail(request, laptop_id):

    user = request.user

    if user.role != "admin":
        return Response(
            {"error": "Only admin allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        laptop = Laptop.objects.select_related(
            "owner",
            "current_holder"
        ).get(id=laptop_id)

    except Laptop.DoesNotExist:
        return Response(
            {"error": "Laptop not found"},
            status=404
        )

    serializer = AdminLaptopSerializer(
        laptop,
        context={"request": request}
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_users(request):

    user = request.user
    # ADMIN ONLY
    if user.role != "admin":
        return Response(
            {"error": "Only admin allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    search = request.GET.get("search")
    role = request.GET.get("role")

    users = User.objects.all()
    # ROLE FILTER
    if role:
        users = users.filter(role=role.upper())
    # SEARCH
    if search:
        users = users.filter(

            Q(username__icontains=search)

            |

            Q(first_name__icontains=search)

            |

            Q(last_name__icontains=search)

            |

            Q(email__icontains=search)

            |

            Q(student_id__icontains=search)
        )

    serializer = AdminUserSerializer(
        users,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_user_detail(request, user_id):
    admin_user = request.user

    if admin_user.role != "admin":
        return Response(
            {"error": "Only admin allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id)

    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=404
        )

    serializer = AdminUserSerializer(
        user,
        context={"request": request}
    )

    # STUDENT LAPTOPS
    laptops = Laptop.objects.filter(owner=user)

    laptop_serializer = AdminLaptopSerializer(
        laptops,
        many=True,
        context={"request": request}
    )

    return Response({
        "user": serializer.data,
        "laptops": laptop_serializer.data
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_transactions(request):
    user = request.user
    if user.role != "admin":
        return Response(
            {"error": "Only admin allowed"},
            status=status.HTTP_403_FORBIDDEN
        )
    action_type = request.GET.get("action_type")
    search = request.GET.get("search")

    transactions = Transaction.objects.select_related(
        "laptop",
        "student",
        "previous_holder",
        "new_holder",
        "scanned_by",
        "laptop__owner",
        "laptop__current_holder"
    ).all()

    # FILTER BY ACTION
    if action_type:
        transactions = transactions.filter(
            action_type=action_type.upper()
        )
    # SEARCH
    if search:
        transactions = transactions.filter(

            Q(student__first_name__icontains=search)

            |

            Q(student__last_name__icontains=search)

            |

            Q(student__student_id__icontains=search)

            |

            Q(laptop__serial_number__icontains=search)

            |

            Q(laptop__brand__icontains=search)
        )

    serializer = AdminTransactionSerializer(
        transactions,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_transaction_detail(request, transaction_id):

    user = request.user

    if user.role != "admin":
        return Response(
            {"error": "Only admin allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        transaction = Transaction.objects.select_related(
            "laptop",
            "student",
            "previous_holder",
            "new_holder",
            "scanned_by",
            "laptop__owner",
            "laptop__current_holder"
        ).get(id=transaction_id)

    except Transaction.DoesNotExist:
        return Response(
            {"error": "Transaction not found"},
            status=404
        )

    serializer = AdminTransactionSerializer(
        transaction,
        context={"request": request}
    )

    return Response(serializer.data)