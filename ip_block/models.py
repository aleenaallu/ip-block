from django.db import models
# Create your models here.

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    # failed_login_attempts = models.PositiveIntegerField()
    # created_at = models.DateTimeField(auto_now_add=True)
    failed_login_attempts = models.IntegerField(null=True)


    def __str__(self):
        return self.ip_address

class BlockedIO(models.Model):
    ip = models.ForeignKey(BlockedIP,on_delete=models.CASCADE)
    io_type = models.CharField(max_length=50)
    blocked_At = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveBigIntegerField(default=10)


class FailedLoginAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    # timestamp = models.DateTimeField(auto_now_add=True)
    count = models.PositiveIntegerField(default=1)


    def __str__(self):
        return self. ip_address
    
#+++++++++++++++++ PERMANENT IP BLOCK +++++++++++++++++++++++++

class PermanentBlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    is_permanently_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.ip_address
    
                                 
