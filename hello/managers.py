from django.db.models.query import QuerySet
from django.conf import settings

class SharedQueries(object):

    """Some queries that are identical for Gallery and Photo."""


class GalleryQuerySet(SharedQueries, QuerySet):
    pass


class PhotoQuerySet(SharedQueries, QuerySet):
    pass
