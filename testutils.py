'''
Shared helpers for the app test suites.
'''


class LoginRequiredTestsMixin:
    '''
    Mix into a TestCase to verify every URL returned by
    get_protected_urls() redirects anonymous users to /signin.
    '''

    def get_protected_urls(self):
        raise NotImplementedError

    def test_anonymous_user_is_redirected_to_signin(self):
        for url in self.get_protected_urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith('/signin'))
