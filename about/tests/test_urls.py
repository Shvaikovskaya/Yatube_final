from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutURLTets(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_urls_exist_at_desired_location(self):
        '''Проверка доступности адресов любому пользователю.'''
        urls = ('/about/author/',
                '/about/tech/',
                )
        for url in urls:
            with self.subTest():
                response = AboutURLTets.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
