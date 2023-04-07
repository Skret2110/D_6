from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import News, Post
from django.shortcuts import redirect
from django.template.loader import render_to_string



@receiver(post_save, sender=News)
def news_created(instance, created, **kwargs):
    if not created:
        return

    emails = User.objects.filter(
        subscriptions__post=instance.post
    ).values_list('email', flat=True)

    subject = f'Новая статья в категории {instance.post}'

    text_content = (
        f'Название: {instance.name}\n'
        
        f'Ссылка: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )
    html_content = (
        f'Название: {instance.name}<br>'
        f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
        f'Ссылка </a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


