from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings


from hello import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    # url(r'^profile/(?P<inv_user_id>[0-9]+)/$', views.profile, name='profile'),
    #
    # # collections urls
    url(r'^collections/$',views.CollectionListView.as_view(template_name="products.html"),name='collections'),
    url(r'^collections/(?P<slug>[\-\d\w]+)/$',views.GalleryDetailView.as_view(template_name="gallery-detail.html"), name='gallery-collection'),
    #categories urls
    url(r'^categories/$',views.CategoryListView.as_view(template_name="products.html"),name='categories'),
    url(r'^categories/(?P<slug>[\-\d\w]+)/$',views.GalleryDetailView.as_view(template_name="gallery-detail.html"), name='gallery-category'),
    #
    url(r'^product/(?P<slug>[\-\d\w]+)/$',views.PhotoDetailView.as_view(template_name="photo-detail.html"),name='photo-detail'),
    #
    #
    # # url(r'^products/$', GalleryListView.as_view(template_name="collections.html"), name='product'),
    # # url(r'^products/$', views.ProductListView.as_view(), name='product_min'),
    url(r'^concepts/$', views.concepts, name='concepts'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^press/$', views.press, name='press'),
]
