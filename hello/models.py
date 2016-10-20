import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils.encoding import force_text, smart_str, filepath_to_uri
from django.utils.functional import curry
from django.utils.safestring import mark_safe
from django.utils.timezone import now

# from autoslug import AutoSlugField
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail import ImageField
# from sortedm2m.fields import SortedManyToManyField

from .managers import GalleryQuerySet, PhotoQuerySet

CATEGORIES = (
        ('Rings','Rings'),
        ('Necklaces','Necklaces'),
        ('Bracelets','Bracelets')
)

size_method_map = {}

class Inv_User(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=30, null=True, blank=False)
    last_name = models.CharField(max_length=30, null=True, blank=False)

    def __unicode__(self):
        return self.user.username
    def __str__(self):
        return self.user.username

class ImageModel(models.Model):
    image = ImageField(
        'image',
        max_length=100,
        upload_to='photos'
    )
    view_count = models.PositiveIntegerField(
        'view count',
        default=0,
        editable=False
    )
    class Meta:
        abstract = True

    def admin_thumbnail(self):
        im = get_thumbnail(self.image, '60x40', crop='center', quality=99)
        return mark_safe('<a href="%s"><img src="%s"></a>' % \
            (self.get_absolute_url(), im.url))
    admin_thumbnail.short_description = 'Thumbnail'

    def image_filename(self):
        return os.path.basename(force_text(self.image.name))

    def increment_count(self):
        self.view_count += 1
        models.Model.save(self)


class Photo(ImageModel):

    title = models.CharField(
        'title',
        max_length=250,
        unique=True
    )
    slug = models.SlugField(
        'slug',
        max_length=250,
    )
    caption = models.TextField(
        'caption',
        blank=True
    )
    date_added = models.DateTimeField(
        'date added',
        auto_now=True
    )
    objects = PhotoQuerySet.as_manager()

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = 'photo'
        verbose_name_plural = 'photos'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('photo-detail', args=[self.slug])

class Gallery(models.Model):
    date_added = models.DateTimeField(
        'date published',
        default=now
    )
    title = models.CharField(
        'title',
        max_length=250,
        unique=True
    )
    slug = models.SlugField(
        'slug',
        max_length=250,
    )
    photos = models.ManyToManyField(
        Photo,
        related_name='gallery',
        verbose_name='photos',
        blank=True
    )
    collection = models.BooleanField(
        'collection',
        default=False
    )
    category = models.BooleanField(
        'category',
        default=False
    )

    objects = GalleryQuerySet.as_manager()

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = 'gallery'
        verbose_name_plural = 'galleries'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.collection:
            return reverse('gallery-collection', args=[self.slug])
        else:
            return reverse('gallery-category', args=[self.slug])

    def photo_count(self):
        return self.photos.count()
    photo_count.short_description = 'count'

    def sample(self):
        if self.photo_count():
            return self.photos.all()[0]
