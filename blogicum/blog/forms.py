from django import forms

from .models import User, Post, Comment


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = (
            'author',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(format='Y-%m-%d %H:%M:%S',
                                            attrs={'type': 'datetime-local'})

        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
