from django.contrib import admin

from .models import Comment, Follow, Group, Post, Profile


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created")
    search_fields = ("text",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author",)
    search_fields = ("user", "author",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "bio", )
    empty_value_display = "-пусто-"
