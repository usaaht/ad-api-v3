from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=255)
    max_visitors = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class DailyVisitor(models.Model):
    ad = models.ForeignKey('Ad', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.location} - {self.date}'

class Ad(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    locations = models.ManyToManyField('Location')

    def __str__(self):
        return self.name
