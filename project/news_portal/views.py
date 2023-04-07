
from django.shortcuts import render, reverse, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import News
from .filters import NewsFilter
from .forms import NewsForm
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .models import Subscription, Post




class NewsList(ListView):
    model = News
    template_name = 'news.html'
    context_object_name = 'news'
    ordering = ['-id']
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        context['filterset'] = self.filterset
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs


class NewsDetail(DetailView):
    model = News
    template_name = 'post.html'
    context_object_name = 'post'


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news_portal.add_news',)
    #raise_exception = True
    form_class = NewsForm
    model = News
    template_name = 'news_edit.html'


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'news_edit.html'
    form_class = NewsForm
    permission_required = ('add_post',)

    def news(self, request, *args, **kwargs):
        form = NewsForm(request.POST)  # поле формы
        news_post_pk = request.POST['news_post']
        sub_text = request.POST.get('text')
        sub_title = request.POST.get('title')
        news_post = News.objects.get(pk=news_post_pk)
        subscribers = news_post.subscribers.all()
        host = request.META.get('HTTP_HOST')

        if form.is_valid():
            news = form.save(commit=False)
            news.save()
        for subscriber in subscribers:
            html_content = render_to_string(
                'news/mail.html', {'user': subscriber, 'text': sub_text[:50], 'post': news, 'title': sub_title, 'host': host}
            )

            msg = EmailMultiAlternatives(
                subject=f'Здравствуй, {subscriber.username}. Новая статья в вашем разделе!',
                body=f'{sub_text[:50]}',

                from_email='fedorenko.i.2110@yandex.ru',
                # Кому отправлять, конкретные адреса рассылки, берем из переменной, либо можно явно прописать
                to=[subscriber.email],
            )

            # прописываем html-шаблон как наполнение письма
            msg.attach_alternative(html_content, "text/html")
            # отправляем письмо
            msg.send()
        # возвращаемся на страницу с постами
        return redirect('/news/')









class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news_portal.change_news',)
    form_class = NewsForm
    model = News
    template_name = 'news_edit.html'


class NewsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news_portal.delete_news',)
    model = News
    template_name = 'news_delete.html'
    queryset = News.objects.all()
    success_url = reverse_lazy('news_list')


class NewsSearch(ListView):
    model = News
    template_name = 'search.html'
    context_object_name = 'search'
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        return context


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, post=post)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                post=post,
            ).delete()

    categories_with_subscriptions = Post.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                post=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )
