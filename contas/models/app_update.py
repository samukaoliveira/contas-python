from django.db import models

class AppUpdate(models.Model):
    version_code = models.IntegerField(unique=True)
    version_name = models.CharField(max_length=30)
    apk_file = models.FileField(upload_to='apks/')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_code']

    def __str__(self):
        return self.version_name