from django.core.paginator import Paginator
from django.db.models import Count
from django.utils.timezone import now


def posts_filtered_by_published(manager_of_posts):
    return manager_of_posts.select_related(
        'category',
        'location',
        'author').filter(is_published=True,
                         category__is_published=True,
                         pub_date__lte=now())


def posts_annotate(posts):
    return posts.annotate(
        comment_count=Count('comments')
    )


def posts_pagination(posts, request):

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')

    return paginator.get_page(page_number)
