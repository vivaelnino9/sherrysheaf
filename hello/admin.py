from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ungettext, ugettext_lazy as _

from .forms import *
from .models import *


admin.site.register(Inv_User)

class GalleryAdminForm(forms.ModelForm):
    model = Gallery


class GalleryAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'date_added', 'photo_count', 'collection','category'
    )
    list_filter = ['date_added',]
    date_hierarchy = 'date_added'
    form = GalleryAdminForm
    view_on_site = False


    def get_urls(self):
        urls = super(GalleryAdmin, self).get_urls()
        add_urls = [
            url(r'^upload_zip/$',
                self.admin_site.admin_view(self.upload_zip),
                name='upload_zip')
        ]
        return add_urls + urls

    def upload_zip(self,request):
        context = {
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request)
        }

        # Handle form request
        if request.method == 'POST':
            form = UploadZipForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(request=request)
                return HttpResponseRedirect('..')
        else:
            form = UploadZipForm()
        context['form'] = form
        context['adminform'] = helpers.AdminForm(form,
                                                 list([(None, {'fields': form.base_fields})]),
                                                 {})
        return render(request, 'admin/hello/gallery/upload_zip.html',context)

admin.site.register(Gallery,GalleryAdmin)

class PhotoAdminForm(forms.ModelForm):
    model = Photo

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added','view_count','admin_thumbnail')
    list_filter = ['date_added',]
    search_fields = ['title', 'caption']
    list_per_page = 10
    form = PhotoAdminForm

admin.site.register(Photo,PhotoAdmin)
