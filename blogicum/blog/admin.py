from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at')
    list_editable = (
        'is_published',
        'description',
        'slug')
    search_fields = ('title',)
    list_filter = ('slug',)
    list_display_links = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'created_at',
        'author',
    )
    list_editable = (
        'post',
        'author',
    )
    search_fields = ('text',)
    list_filter = ('author',)
    list_display_links = ('text',)


class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = (
        'name',
        'is_published',
        'created_at')
    list_editable = (
        'is_published',)
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at')
    list_editable = (
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published')
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
