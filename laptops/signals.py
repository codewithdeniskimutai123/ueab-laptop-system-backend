from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.db import transaction

from .models import Laptop
@receiver(pre_save, sender=Laptop)
def capture_old_holder(sender, instance, **kwargs):

    if instance.pk:
        try:
            instance._old_holder = Laptop.objects.get(pk=instance.pk).current_holder
        except Laptop.DoesNotExist:
            instance._old_holder = None
    else:
        instance._old_holder = None


def send_registration_email(instance):

    try:
        if not instance.qr_code or not instance.qr_code.name:
            print("QR NOT READY - skipping email")
            return

        file_path = instance.qr_code.path

        with open(file_path, 'rb') as f:
            qr_data = f.read()

        # ---------------- OWNER EMAIL ----------------
        owner_email = EmailMessage(
            subject="Laptop Registration Successful",
            body=f"""
Hello {instance.owner.first_name},

Your laptop has been successfully registered.
LAPTOP DETAILS
Brand: {instance.brand}
Serial: {instance.serial_number}
""",
            to=[instance.owner.email]
        )

        owner_email.attach(
            f"{instance.serial_number}.png",
            qr_data,
            "image/png"
        )

        owner_email.send(fail_silently=True)

        # ---------------- CURRENT HOLDER EMAIL ----------------
        if instance.current_holder and instance.current_holder != instance.owner:

            holder_email = EmailMessage(
                subject="Laptop Assignment Notification",
                body=f"""
Hello {instance.current_holder.first_name},

A laptop has been assigned to you.
LAPTOP DETAILS
Brand: {instance.brand}
Serial: {instance.serial_number}
""",
                to=[instance.current_holder.email]
            )

            holder_email.attach(
                f"{instance.serial_number}.png",
                qr_data,
                "image/png"
            )

            holder_email.send(fail_silently=False)

        print("EMAIL SENT SUCCESSFULLY ✔")

    except Exception as e:
        print("EMAIL FAILED ❌:", e)

# HANDLE REGISTRATION
@receiver(post_save, sender=Laptop)
def send_laptop_qr_email(sender, instance, created, **kwargs):

    if not created:
        return

    print("Signal registered (API safe version)...")

    transaction.on_commit(lambda: send_registration_email(instance))

# HANDLE HOLDER CHANGE (TRANSFER LOGIC)

@receiver(post_save, sender=Laptop)
def handle_holder_change(sender, instance, created, **kwargs):

    if created:
        return

    old_holder = getattr(instance, "_old_holder", None)
    new_holder = instance.current_holder

    if old_holder != new_holder:

        print("Holder changed → sending update emails")

        # ---------------- NEW HOLDER ----------------
        if new_holder:

            EmailMessage(
                subject="Laptop Assignment Update",
                body=f"""
Hello {new_holder.first_name},

You are now the current holder of this laptop.
LAPTOP DETAILS
Brand: {instance.brand}
Serial: {instance.serial_number}
""",
                to=[new_holder.email]
            ).send(fail_silently=False)

        # ---------------- OLD HOLDER ----------------
        if old_holder:

            EmailMessage(
                subject="Laptop Reassignment Notice",
                body=f"""
Hello {old_holder.first_name},

You are no longer the current holder of this laptop.
LAPTOP DETAILS
Brand: {instance.brand}
Serial: {instance.serial_number}
""",
                to=[old_holder.email]
            ).send(fail_silently=True)