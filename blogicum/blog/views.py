# from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from django.urls import reverse
from django.views.generic import UpdateView, CreateView, DeleteView

from django.db.models import Count

from .forms import CommentForm, ProfileForm, PostForm
from .models import Category, Comment, Post, User


def profile_username(request, username):
    profile = get_object_or_404(
        User,
        username=username,
    )
    posts_not_filtered = profile.posts.all()
    if profile == request.user:
        posts = posts_not_filtered
    else:
        posts = profile.posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now()
        )

    posts = posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html',
                  {'profile': profile, 'page_obj': page_obj})


def edit_profile_username(request):
    instance = get_object_or_404(
        User,
        username=request.user.username,
    )
    form = ProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()

    return render(request, 'blog/user.html', context)


def posts_filtered_by_published(manager_of_posts):
    return manager_of_posts.select_related(
        'category',
        'location',
        'author').filter(is_published=True,
                         category__is_published=True,
                         pub_date__lte=now())


def index(request):
    post_list = posts_filtered_by_published(
        Post.objects
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post_not_filtered = get_object_or_404(
        Post.objects.select_related(
            'category',
            'location',
            'author'
        ).all(),
        pk=post_id
    )
    if post_not_filtered.author == request.user:
        post = post_not_filtered
    else:
        post = get_object_or_404(
            posts_filtered_by_published(Post.objects),
            pk=post_id
        )
    context = {'post': post,
               'form': CommentForm(),
               'comments': post.comments.select_related('author')}

    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = posts_filtered_by_published(
        category.posts.all()
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,
                  'blog/category.html',
                  {'page_obj': page_obj, 'category': category})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    template_name = 'blog/create.html'


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user
    
    def handle_no_permission(self):
        object = self.get_object()
        return redirect('blog:post_detail', object.id)


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.author})


class CommentCreateView(LoginRequiredMixin, CreateView):
    cur_post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.cur_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.cur_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.cur_post.pk})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    cur_post = None
    model = Comment
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.cur_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.cur_post.pk})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    cur_post = None
    model = Comment
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.cur_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.cur_post.pk})
