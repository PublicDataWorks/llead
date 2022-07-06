import json

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from feedbacks.models import Feedback


class FeedbackViewSet(ViewSet):
    def create(self, request):
        feedback = json.loads(request.body)

        email = feedback.get('email')
        message = feedback.get('message')

        item = {
            'email': email,
            'message': message,
        }

        Feedback.objects.create(**item)

        context = {
            "message": f"Message from {email}: {message}"
        }

        send_mail(
            subject="IPNO message from contact page",
            from_email=settings.FEEDBACK_TO_EMAIL,
            recipient_list=[settings.FEEDBACK_TO_EMAIL, email],
            html_message=render_to_string("email/dynamic_email.html", context),
            message=render_to_string("email/dynamic_email.html", context)
        )

        return Response({"detail": "Your message has been sent"})
