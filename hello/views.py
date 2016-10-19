from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import formats

from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView


# from .forms import *
from .models import *


def index(request):
    return render(request, 'index.html')


def register(request):
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and Inv_User.
        user_form = UserForm(data=request.POST)
        inv_user_form = Inv_UserForm(data=request.POST);

        # If the two forms are valid...
        if user_form.is_valid() and inv_user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)

            # Now sort out the Inv_User instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            inv_user = inv_user_form.save(commit=False)
            inv_user.user = user
            user.first_name = inv_user.first_name
            user.last_name = inv_user.last_name

            # Now we save the User and Inv_User model instance.
            user.save()
            inv_user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, inv_user_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        inv_user_form = Inv_UserForm()

    # Render the template depending on the context.
    return render(request,
                  'register.html',
                  {'user_form': user_form, 'inv_user_form': inv_user_form, 'registered': registered} )
def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
        # because the request.POST.get('<variable>') returns None, if the value does not exist,
        # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active?
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user to the products page.
                login(request, user)
                #return render(request,"products.html")
                return HttpResponseRedirect(reverse('collection'))
            else:
                # An inactive account was used - no logging in!
                return render(request, 'redirect.html', {
                    'title': 'Account Disabled',
                    'heading': 'Banned',
                    'content': 'Your account has been disabled. Contact an administrator.',
                    'url_arg': 'index',
                    'url_text': 'Back to homepage'
            })

        else:
            # Bad login details were provided. So we can't log the user in.
            return render(request, 'redirect.html', {
                'title': 'Invalid Login',
                'heading': 'Incorrect Login',
                'content': 'Invalid login details for: {0}'.format(username),
                'url_arg': 'login',
                'url_text': 'Back to login'
            })
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        return render(request, 'login.html', {})

@login_required
def profile(request, inv_user_id):
    inv_user = get_object_or_404(Inv_User, pk=inv_user_id)

    return render(request, 'profile.html', {'inv_user': inv_user})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('product'))


class CollectionListView(ListView):
    # queryset = Gallery.objects.on_site().is_public()
    paginate_by = 20
    queryset = Gallery.objects.filter(collection=True)
class CategoryListView(ListView):
    # queryset = Gallery.objects.on_site().is_public()
    paginate_by = 20
    queryset = Gallery.objects.filter(category=True)

class GalleryDetailView(DetailView):
    queryset = Gallery.objects.all()
class PhotoDetailView(DetailView):
    queryset = Photo.objects.all()


def concepts(request):
    return render(request,"concepts.html")
def about(request):
    return render(request,"about.html")
def contact(request):
    return render(request,"contact.html")
def press(request):
    return render(request,"press.html")
