from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from SocialApp.forms import AuthenticateForm, UserCreateForm, PostForm
from SocialApp.models import Post
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        post_form = PostForm()
        user = request.user
        posts_self = Post.objects.filter(user=user.id)
        posts_buddies = Post.objects.filter(user__userprofile__in=user.profile.follows.all)
        posts = posts_self | posts_buddies
 
        return render(request,
                      'buddies.html',
                      {'post_form': post_form, 'user': user,
                       'posts': posts,
                       'next_url': '/', })
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()
 
        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')
 
 
def logout_view(request):
    logout(request)
    return redirect('/')

def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')

@login_required
def submit(request):
    if request.method == "POST":
        post_form = PostForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect(next_url)
        else:
            return public(request, post_form)
    return redirect('/')

@login_required
def public(request, post_form=None):
    post_form = post_form or PostForm()
    post = Post.objects.reverse()[:10]
    return render(request,
                  'public.html',
                  {'post_form': post_form, 'next_url': '/posts',
                   'posts': post, 'username': request.user.username})
                  
def get_latest(user):
    try:
        return user.post_set.order_by('-id')[0]
    except IndexError:
        return ""
 
 
@login_required
def users(request, username="", post_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        posts = Post.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'posts': posts, })
        return render(request, 'user.html', {'user': user, 'posts': posts, 'follow': True, })
    users = User.objects.all().annotate(post_count=Count('post'))
    posts = map(get_latest, users)
    obj = zip(users, posts)
    post_form = post_form or PostForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'post_form': post_form,
                   'username': request.user.username, })
                  
@login_required
def follow(request):
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')

