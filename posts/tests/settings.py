from django.urls import reverse

NON_EXISTENT_URL = reverse('group_posts', kwargs={'slug': 'NON_EXISTENT'})
CACHE_TIMEOUT = 21
WRITER = 'writer'
READER = 'reader'
GROUP_1_TITLE = 'Новое сообщество 1'
GROUP_2_TITLE = 'Новое сообщество 2'
GROUP_3_TITLE = 'Новое сообщество 3'
GROUP_1_SLUG = 'test_group_1'
GROUP_2_SLUG = 'test_group_2'
GROUP_3_SLUG = 'test_group_3'
GROUP_1_DESCR = 'Описание сообщества 1'
GROUP_2_DESCR = 'Описание сообщества 2'
GROUP_3_DESCR = 'Описание сообщества 3'

INDEX_URL = reverse('index')
GROUPS_INDEX_URL = reverse('groups_index')
NEW_POST_URL = reverse('new_post')
NEW_GROUP_POST_URL = reverse('new_group_post',
                             kwargs={'slug': 'test_group_1'})
NEW_GROUP_URL = reverse('new_group')
PROFILE_URL = reverse('profile', kwargs={'username': 'writer'})

GROUP_1_URL = reverse('group_posts', kwargs={'slug': GROUP_1_SLUG})
GROUP_2_URL = reverse('group_posts', kwargs={'slug': GROUP_2_SLUG})

SAVED_POSTS_URL = reverse('saved_posts')
FOLLOW_INDEX_URL = reverse('follow_index')
FOLLOW_URL = reverse('profile_follow', kwargs={'username': 'reader'})
FOLLOW_FOLLOWED_URL = reverse('profile_follow', kwargs={'username': 'writer'})
UNFOLLOW_URL = reverse('profile_unfollow', kwargs={'username': 'writer'})
UNFOLLOW_UNFOLLOWED_URL = reverse('profile_unfollow', kwargs={'username': 'reader'})

SEARCH_URL = reverse('search')
