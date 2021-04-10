import operator
from functools import reduce
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, GroupForm, GroupPostForm, PostForm
from .models import Follow, Group, Post, User
from .settings import PAGE_SIZE


def add_paginator_to_context(request, posts):
    paginator = Paginator(posts, PAGE_SIZE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return {"page": page}


def index(request):
    """View-функция для главной страницы."""
    posts = Post.objects.all()
    context = add_paginator_to_context(request, posts)
    context["index"] = True
    return render(request, "index.html", context)


def groups_index(request):
    """View-функция для главной страницы."""
    groups = Group.objects.all()
    context = {"groups": groups}
    return render(request, "groups_index.html", context)


def group_posts(request, slug):
    """View-функция для страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = add_paginator_to_context(request, posts)
    context["group"] = group
    return render(request, "group.html", context)


@login_required
def saved_posts(request):
    """View-функция для сохранённых публикаций."""
    user = request.user
    posts = user.saved_posts.all()
    context = add_paginator_to_context(request, posts)
    context["saved"] = True
    return render(request, "saved.html", context)


@login_required
def new_post(request, slug=None):
    """View-функция для создания новой публикации."""
    context = {}
    if slug is not None:
        group = get_object_or_404(Group, slug=slug)
        context["group"] = group
        form = GroupPostForm(request.POST or None, files=request.FILES or None)
        form.instance.group = group
    else:
        form = PostForm(request.POST or None, files=request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.instance.author = request.user
        form.save()
        if "next" in request.GET:
            return redirect(request.GET["next"])
        if slug is not None:
            return redirect("group_posts", slug=slug)
        return redirect("index")
    context["form"] = form
    return render(request, "new_post.html", context)


@login_required
def new_group(request):
    """View-функция для создания нового сообщества."""
    context = {}
    form = GroupForm(request.POST or None,)
    if request.method == "POST" and form.is_valid():
        form.save()
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return redirect("groups_index")
    context["form"] = form
    return render(request, "new_group.html", context)


@login_required
def save_post(request, post_id):
    """View-функция для сохранения публикации."""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    post.saved.add(user)
    post.save()
    if request.META.get("HTTP_REFERER"):
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return redirect("saved_posts")


@login_required
def remove_post(request, post_id):
    """View-функция для удаления пибликации из сохранённых."""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    post.saved.remove(user)
    post.save()
    if request.META.get("HTTP_REFERER"):
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return redirect("saved_posts")


@login_required
def post_edit(request, username, post_id):
    """View-функция для редактирования публикации."""
    if request.user.username != username:
        return redirect("post", username=username, post_id=post_id)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "new_post.html", {"form": form, "post": post})


@login_required
def post_delete(request, username, post_id):
    """View-функция для удаления публикации."""
    if request.user.username != username:
        return redirect("post", username=username, post_id=post_id)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    post.delete()
    if request.META.get("HTTP_REFERER"):
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return redirect("index")


def post_search(request):
    """View-функция для поиска по публикациям."""
    query = None
    if "query" in request.GET:
        query = request.GET["query"]
        words = query.split()
        posts = Post.objects.filter(reduce(operator.or_,
                                           (Q(text__icontains=word)
                                            for word in words)))
    else:
        posts = Post.objects.all()
    context = add_paginator_to_context(request, posts)
    context["query"] = query
    context["index"] = True
    return render(request, "index.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    user = request.user
    following = author.following.filter(user__username=user.username).count()
    context = add_paginator_to_context(request, posts)
    context["author"] = author
    context["following"] = following
    context["following_count"] = author.following.count()
    context["follower_count"] = author.follower.count()
    context["posts_count"] = posts.count()
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    """функция для просмотра поста."""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    comments = post.comments.all()
    form = CommentForm()
    context = {"author": author,
               "post": post,
               "comments": comments,
               "form": form, }
    return render(request, "post.html", context)


@login_required
def add_comment(request, username, post_id):
    """View-функция для добавления комментария."""
    if request.method != "POST":
        return redirect("post", username=username, post_id=post_id)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    form = CommentForm(request.POST)
    if request.method == "POST" and form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return redirect("post", username=username, post_id=post_id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author == user:
        return redirect("profile", username=username)
    if user.follower.filter(author=author).count() == 0:
        Follow.objects.create(author=author,
                              user=user)
    if request.META.get("HTTP_REFERER"):
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = Follow.objects.get(author=author,
                                user=user)
    follow.delete()
    if request.META.get("HTTP_REFERER"):
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    return redirect("profile", username=username)


@login_required
def follow_index(request):
    """View-функция для отображения подписок."""
    user = request.user
    following = user.follower.all().values_list("author")
    posts = Post.objects.filter(author__in=following)
    context = add_paginator_to_context(request, posts)
    context["follow"] = True
    return render(request, "follow_index.html", context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    return render(request, "misc/500.html",
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)
