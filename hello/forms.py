import os
import zipfile
try:
    from zipfile import BadZipFile
except ImportError:
    # Python 2.
    from zipfile import BadZipfile as BadZipFile
try:
    import Image
except ImportError:
    from PIL import Image

from django import forms
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from io import BytesIO

from .models import User, Inv_User, Photo, Gallery



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class Inv_UserForm(forms.ModelForm):
    class Meta:
        model = Inv_User
        fields = ('first_name', 'last_name')

class UploadZipForm(forms.Form):
    zip_file = forms.FileField()

    title = forms.CharField(
        label='Title',
        required=False,
        help_text=''
    )

    gallery = forms.ModelChoiceField(
        Gallery.objects.all(),
        label='Gallery',
        required=False,
        help_text=
            'Select a gallery to add these images to. Leave this empty to'
            'create a new gallery from the supplied title.'
    )
    collection = forms.BooleanField(
        label='Collection',
        required=False
    )
    category = forms.BooleanField(
        label='Category',
        required=False
    )

    def clean_zip_file(self):
        """Open the zip file a first time, to check that it is a valid zip archive.
        We'll open it again in a moment, so we have some duplication, but let's focus
        on keeping the code easier to read!
        """
        zip_file = self.cleaned_data['zip_file']
        try:
            zip = zipfile.ZipFile(zip_file)
        except BadZipFile as e:
            raise forms.ValidationError(str(e))
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            raise forms.ValidationError('"%s" in the .zip archive is corrupt.' % bad_file)
        zip.close()  # Close file in all cases.
        return zip_file

    def clean_title(self):
        title = self.cleaned_data['title']
        if title and Gallery.objects.filter(title=title).exists():
            raise forms.ValidationError(_('A gallery with that title already exists.'))
        return title

    def clean(self):
        cleaned_data = super(UploadZipForm, self).clean()
        if not self['title'].errors:
            # If there's already an error in the title, no need to add another
            # error related to the same field.
            if not cleaned_data.get('title', None) and not cleaned_data['gallery']:
                raise forms.ValidationError(
                    _('Select an existing gallery, or enter a title for a new gallery.'))
        return cleaned_data

    def save(self, request=None, zip_file=None):
        if not zip_file:
            zip_file = self.cleaned_data['zip_file']
        zip = zipfile.ZipFile(zip_file,'r')
        count = 1
        if self.cleaned_data['gallery']:
            logger.debug('Using pre-existing gallery.')
            gallery = self.cleaned_data['gallery']
        else:
            logger.debug(
                force_text('Creating new gallery "{0}".').format(self.cleaned_data['title'])
            )
            # make if statement for if there is collection/category
            gallery = Gallery.objects.create(
                title=self.cleaned_data['title'],
                slug=slugify(self.cleaned_data['title']),
                collection = self.cleaned_data['collection'],
                category = self.cleaned_data['category']
            )
        # number = randint(0,1000)
        found_image = False
        for filename in sorted(zip.namelist()):
            # Get file extension
            _, file_extension = os.path.splitext(filename)
            file_extension = file_extension.lower()

            # Skip non jpg files
            if not file_extension or file_extension != '.jpg':
                continue
            logger.debug('Reading file "{0}".'.format(filename))

            if filename.startswith('__') or filename.startswith('.'):
                logger.debug('Ignoring file "{0}".'.format(filename))
                continue

            data = zip.read(filename)

            if not len(data):
                logger.debug('File "{0}" is empty.'.format(filename))
                continue

            photo_title_root = self.cleaned_data['title'] if self.cleaned_data['title'] else gallery.title

            # A photo might already exist with the same slug. So it's somewhat inefficient,
            # but we loop until we find a slug that's available.
            # while True:
            #     photo_title = ' '.join([photo_title_root, str(number)])
            #     slug = slugify(photo_title)
            #     if Photo.objects.filter(slug=slug).exists():
            #         number = randint(0,1000)
            #         continue
            #     break
            while True:
                photo_title = ' '.join([photo_title_root, str(count)])
                slug = slugify(photo_title)
                if Photo.objects.filter(slug=slug).exists():
                    count += 1
                    continue
                break

            photo = Photo(title=photo_title,
                          slug=slug,
                          date_added=now
                    )

            # Basic check that we have a valid image.
            try:
                file = BytesIO(data)
                opened = Image.open(file)
                opened.verify()
            except Exception:
                # Pillow (or PIL) doesn't recognize it as an image.
                # If a "bad" file is found we just skip it.
                # But we do flag this both in the logs and to the user.
                logger.error('Could not process file "{0}" in the .zip archive.'.format(
                    filename))
                if request:
                    messages.warning(request,
                                     _('Could not process file "{0}" in the .zip archive.').format(
                                         filename),
                                     fail_silently=True)
                continue

            contentfile = ContentFile(data)
            photo.image.save(filename, contentfile)
            photo.save()
            gallery.photos.add(photo)
            count += 1

        zip.close()

        # if request:
        #     messages.success(request,
        #                      _('The photos have been added to gallery "{0}".').format(
        #                          gallery.title),
        #                      fail_silently=True)
