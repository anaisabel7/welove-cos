from django.db import models

# Create your models here.


class Source(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Quote(models.Model):
    quote_text = models.CharField(max_length=600)
    selected = models.BooleanField(default=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)

    def __str__(self):
        returned_str = "A quote from %s" % (self.source.name)
        return returned_str
