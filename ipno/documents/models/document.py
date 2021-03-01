from django.db import models

from utils.models import TimeStampsModel


class Document(TimeStampsModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    document_type = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    preview_image_url = models.CharField(max_length=255, null=True, blank=True)
    incident_date = models.DateField(null=True)
    pages_count = models.IntegerField(null=True, blank=True)
    text_content = models.TextField(blank=True)

    officers = models.ManyToManyField('officers.Officer', blank=True)
    departments = models.ManyToManyField('departments.Department', blank=True)
