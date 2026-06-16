from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=200, blank=True)
    url = models.URLField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
