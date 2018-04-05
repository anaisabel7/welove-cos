from django.db import models

# Create your models here.


class Quote(models.Model):
    quote_text = models.CharField(max_length=600)
    source = models.CharField(max_length=100)
    selected = models.BooleanField(default=False)

    def __str__(self):
        returned_str = "A quote from %s" % (self.source)
        return returned_str
