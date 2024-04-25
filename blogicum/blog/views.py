from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView

from .forms import CommentForm, ProfileForm, PostForm
from .models import Category, Post, User
from .posts_utils import (posts_filtered_by_published, posts_annotate,
                          posts_pagination)
from .mixin import OnlyAuthorMixin, PostMixin, CommentMixin


def profile_username(request, username):
    profile = get_object_or_404(
        User,
        username=username,
    )
    posts = posts_annotate(profile.posts.all())
    if profile != request.user:
        posts = posts_filtered_by_published(
            posts
        )
    return render(request, 'blog/profile.html',
                  {'profile': profile,
                   'page_obj': posts_pagination(posts, request)})


def edit_profile_username(request, username):
    profile = get_object_or_404(
        User,
        username=username,
    )
    if profile != request.user:
        return redirect('blog:profile', username=profile.username)

    form = ProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=profile.username)

    return render(request, 'blog/user.html', {'form': form})


def index(request):
    return render(
        request,
        'blog/index.html',
        {'page_obj': posts_pagination(
            posts_filtered_by_published(
                posts_annotate(Post.objects)
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
               'comments': post.comments.select_related('author')}

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
            )
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


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs[self.pk_url_kwarg]})


class PostDeleteView(PostMixin, DeleteView):
    pass


class CommentCreateView(CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass


class RegistrationCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
