# from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from django.urls import reverse
from django.views.generic import UpdateView, CreateView, DeleteView

from .forms import CommentForm, ProfileForm, PostForm
from .models import Category, Comment, Post, User
from .utils import (posts_filtered_by_published, posts_annotate,
                    posts_pagination)
from .mixin import OnlyAuthorMixin, PostMixin, CommentMixin


def profile_username(request, username):
    profile = get_object_or_404(
        User,
        username=username,
    )
    posts = posts_annotate(profile.posts.all()).order_by('-pub_date')
    if profile != request.user:
        posts = posts_filtered_by_published(
            posts
        )
    return render(request, 'blog/profile.html',
                  {'profile': profile,
                   'page_obj': posts_pagination(posts, request)})


def edit_profile_username(request):
    instance = get_object_or_404(
        User,
        username=request.user.username,
    )
    form = ProfileForm(request.POST or None, instance=instance)      # не понял комментария(
    context = {'form': form}
    if form.is_valid():
        form.save()

    return render(request, 'blog/user.html', context)


def index(request):
    return render(
        request,
        'blog/index.html',
        {'page_obj': posts_pagination(
            posts_filtered_by_published(
                posts_annotate(Post.objects).order_by('-pub_date')
            ),
            request
        )}
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related(
            'category',
            'location',
            'author'
        ).all(),
        pk=post_id
    )
    if post.author != request.user:
        post = get_object_or_404(
            posts_filtered_by_published(Post.objects),
            pk=post_id
        )
    context = {'post': post,
               'form': CommentForm(),
               'comments': post.comments.select_related('author')} # переделать ключ на page_obj , чтобы сделать пагинацию, но для этого надо поправить шаблон

    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    page_obj = posts_pagination(
        posts_filtered_by_published(
            posts_annotate(
                category.posts.all()
            ).order_by('-pub_date')
        ),
        request
    )

    return render(request,
                  'blog/category.html',
                  {'page_obj': page_obj, 'category': category})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# class OnlyAuthorMixin(UserPassesTestMixin):

#     def test_func(self):
#         return self.get_object().author == self.request.user

#     def handle_no_permission(self):
#         return redirect('blog:post_detail', self.get_object().id)


class PostUpdateView(PostMixin, UpdateView):
    # model = Post
    # pk_url_kwarg = 'post_id'
    # form_class = PostForm
    # template_name = 'blog/create.html'
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(PostMixin, DeleteView):
    pass
    # model = Post
    # template_name = 'blog/create.html'

    # def get_success_url(self):
    #     return reverse('blog:profile', kwargs={'username': self.object.author})


class CommentCreateView(CommentMixin, CreateView):
    # cur_post = None
    # model = Comment
    # form_class = CommentForm

    # def dispatch(self, request, *args, **kwargs):
    #     self.cur_post = get_object_or_404(Post, pk=kwargs['post_id'])
    #     return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.cur_post
        return super().form_valid(form)

    # def get_success_url(self):
    #     return reverse('blog:post_detail',
    #                    kwargs={'post_id': self.cur_post.pk})


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass
    # cur_post = None
    # model = Comment
    # pk_url_kwarg = 'comment_id'
    # form_class = CommentForm

    # def dispatch(self, request, *args, **kwargs):
    #     self.cur_post = get_object_or_404(Post, pk=kwargs['post_id'])
    #     return super().dispatch(request, *args, **kwargs)

    # template_name = 'blog/comment.html'

    # def get_success_url(self):
    #     return reverse('blog:post_detail',
    #                    kwargs={'post_id': self.cur_post.pk})


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass
    # cur_post = None
    # model = Comment
    # pk_url_kwarg = 'comment_id'
    # form_class = CommentForm

    # def dispatch(self, request, *args, **kwargs):
    #     self.cur_post = get_object_or_404(Post, pk=kwargs['post_id'])
    #     return super().dispatch(request, *args, **kwargs)

    # template_name = 'blog/comment.html'

    # def get_success_url(self):
    #     return reverse('blog:post_detail',
    #                    kwargs={'post_id': self.cur_post.pk})
