from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Source(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=300)

    def __str__(self):
        return self.name


class Quote(models.Model):
    quote_text = models.CharField(max_length=600, unique=True)
    selected = models.BooleanField(default=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)
    popularity = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Only one Quote instance can be 'selected'
        if self.selected:
            Quote.objects.filter(selected=True).update(selected=False)

        super().save(*args, **kwargs)

    def __str__(self):
        returned_str = "A quote from %s" % (self.source.name)
        return returned_str


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=False)
    favourite_quote = models.ForeignKey(
        Quote, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        returned_str = "The profile of %s" % (self.user)
        return returned_str


class Message(models.Model):
    message_text = models.TextField()
    displayed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Only one Message instance can be 'displayed'
        if self.displayed:
            Message.objects.filter(displayed=True).update(displayed=False)

        super().save(*args, **kwargs)

    def __str__(self):
        returned_str = "Site message: {}".format(self.message_text)
        return returned_str
