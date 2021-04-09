from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('saved/', views.saved_posts, name='saved_posts'),
    path('search/', views.post_search, name='search'),
    path('new/', views.new_post, name='new_post'),
    path('new/<slug:slug>/', views.new_post, name='new_group_post'),
    path('post/save/<int:post_id>/', views.save_post, name='save_post'),
    path('post/remove/<int:post_id>/', views.remove_post, name='remove_post'),
    path('groups/', views.groups_index, name='groups_index'),
    path('groups/new/', views.new_group, name='new_group'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('follow/', views.follow_index, name='follow_index'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/delete/',
         views.post_delete,
         name='post_delete'),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'),
    path("<str:username>/<int:post_id>/comment/",
         views.add_comment,
         name="add_comment"),
    path('<str:username>/', views.profile, name='profile'),
    path("<str:username>/follow/",
         views.profile_follow,
         name="profile_follow"),
    path("<str:username>/unfollow/",
         views.profile_unfollow,
         name="profile_unfollow"),
]
