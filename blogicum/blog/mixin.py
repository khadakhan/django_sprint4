from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Post, Comment


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(LoginRequiredMixin, OnlyAuthorMixin):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.get_object().id)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.author})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CommentMixin(LoginRequiredMixin):
    cur_post = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.cur_post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.cur_post.pk})
