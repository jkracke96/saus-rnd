from django.db import models
from django.conf import settings
import helpers.billing

User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return str(self.user.username)
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            email = self.user.email
            if email != "" and email is not None:
                name = self.user.username
                stripe_id = helpers.billing.create_customer(
                    name=name,
                    email=email,
                    raw=False
                )
                self.stripe_id = stripe_id
        super().save(*args, **kwargs)
