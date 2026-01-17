from django.conf import settings
from django.core.mail import send_mail

from users.models import CustomUser


def notify_admins_of_new_user(user):
    """
    Notify company admins when a new user registers to join their organization.
    Sends email with user details and approval instructions.
    """
    admins = CustomUser.objects.filter(tenant=user.tenant, role="admin", is_active=True)
    if not admins:
        return

    subject = f"[ClinicCloud] New User Pending Approval: {user.username}"
    message = (
        f"Hello Admin,\n\n"
        f"A new user has requested to join your organization: '{user.tenant.name}'.\n\n"
        f"User Details:\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  Username: {user.username}\n"
        f"  Email: {user.email}\n"
        f"  Role: {user.role}\n"
        f"  Registered: {user.date_joined.strftime('%B %d, %Y at %I:%M %p')}\n"
        f"  Status: Pending Approval\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Action Required:\n"
        f"To approve or reject this user, please log in to your admin dashboard:\n"
        f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://your-domain.com'}/admin/users/customuser/{user.id}/change/\n\n"
        f"Security Note:\n"
        f"Please verify that you know this person before approving their access.\n"
        f"Unauthorized access to patient data may violate HIPAA and other regulations.\n\n"
        f"Best regards,\n"
        f"ClinicCloud Team"
    )

    from_email = (
        settings.DEFAULT_FROM_EMAIL
        if hasattr(settings, "DEFAULT_FROM_EMAIL")
        else "noreply@cliniccloud.com"
    )
    recipient_list = [admin.email for admin in admins if admin.email]

    if recipient_list:
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            # Log error but don't block registration
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send admin notification email: {str(e)}")


def notify_user_approved(user):
    """
    Notify user when their account has been approved by an admin.
    """
    if not user.email:
        return

    subject = f"[ClinicCloud] Your Account Has Been Approved"
    message = (
        f"Hello {user.username},\n\n"
        f"Great news! Your account has been approved by an administrator at '{user.tenant.name}'.\n\n"
        f"You can now log in and start using ClinicCloud:\n"
        f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://your-domain.com'}/accounts/login/\n\n"
        f"Your Account Details:\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  Username: {user.username}\n"
        f"  Email: {user.email}\n"
        f"  Organization: {user.tenant.name}\n"
        f"  Role: {user.role}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"If you have any questions, please contact your organization administrator.\n\n"
        f"Welcome to ClinicCloud!\n"
        f"The ClinicCloud Team"
    )

    from_email = (
        settings.DEFAULT_FROM_EMAIL
        if hasattr(settings, "DEFAULT_FROM_EMAIL")
        else "noreply@cliniccloud.com"
    )

    try:
        send_mail(subject, message, from_email, [user.email], fail_silently=False)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send user approval email: {str(e)}")


def notify_user_rejected(user, reason=""):
    """
    Notify user when their account registration has been rejected.
    """
    if not user.email:
        return

    subject = f"[ClinicCloud] Account Registration Update"
    message = (
        f"Hello {user.username},\n\n"
        f"We regret to inform you that your request to join '{user.tenant.name}' has not been approved at this time.\n\n"
    )

    if reason:
        message += f"Reason: {reason}\n\n"

    message += (
        f"If you believe this is an error or have questions, please contact the administrator "
        f"of '{user.tenant.name}' directly.\n\n"
        f"Thank you for your interest in ClinicCloud.\n\n"
        f"Best regards,\n"
        f"The ClinicCloud Team"
    )

    from_email = (
        settings.DEFAULT_FROM_EMAIL
        if hasattr(settings, "DEFAULT_FROM_EMAIL")
        else "noreply@cliniccloud.com"
    )

    try:
        send_mail(subject, message, from_email, [user.email], fail_silently=False)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send user rejection email: {str(e)}")
