from django.shortcuts import render, redirect
from . import util
from markdown2 import Markdown
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

m = Markdown()

#Create your views here.
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password =  request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request,"Username or password is incorrect.")
    
    return render(request, 'blog/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url="login")
def home(request):
    return render(request, 'blog/posts.html', {
                    "username":request.user,
                    "posts": util.list_posts(request.user)
                })

@login_required(login_url="login")
def post(request, title):
    return render(request, 'blog/user_post.html',{
        "title":title,
        "username":request.user,
        "post":util.get_post(request.user, title),
        "viewer_post": m.convert(util.get_post(request.user, title))
    })

def create_account(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            util.save_post(request.POST.get("username"),"Welcome!","This is a sample post that you can edit or delete.")
            messages.info(request,"Account created!")  
        else:
            messages.error(request, "Choose another username.")      
    return render(request, 'blog/register.html', {
        "form":CreateUserForm()
    })

@login_required(login_url="login")
def edit(request, title):
    return render(request,"blog/edit.html", {
        "title":title,
        "username":request.user,
        "post":util.get_post(request.user, title)

    })

@login_required(login_url="login")
def new(request):
    return render(request,"blog/new.html")

def save(request):
    title = request.POST.get("title")
    post = request.POST.get("post")
    util.save_post(request.user, title, post)
    return redirect('user_post',title=title)

def delete(request, title):
    if request.method == 'POST':
        util.delete_post(request.user,title)
        return redirect('home')
    
    return render(request,'blog/delete.html',{
        "title":title
    })