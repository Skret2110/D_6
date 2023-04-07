import datetime

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Sum


class News(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )
    description = models.TextField()
    post = models.ForeignKey(
        to='Post',
        on_delete=models.CASCADE,
        related_name='news',
    )
    publish = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.name.title()}: {self.description[:30]}'

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])


class Post(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribers')

    def __str__(self):
        return self.name.title()


class Subscription(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    post = models.ForeignKey(
        to='Post',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )

