import unittest
from machinehub.server.app import webapp
import base64


errors = {200: '200 OK',
          401: '401 UNAUTHORIZED',
          404: '404 NOT FOUND'
          }


class BasicTest(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app.test_client()

    def tearDown(self):
        pass

    def auth_test(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status, errors[401])
        rv = self.open_with_auth('/', 'GET', 'guaca', 'mole')
        self.assertEqual(rv.status, errors[401])
        rv = self.open_with_auth('/', 'GET')
        self.assertEqual(rv.status, errors[200])

    def not_found_test(self):
        rv = self.app.get('/not_found')
        self.assertEqual(rv.status, errors[404])

    def open_with_auth(self, url, method,
                       username='admin', password='admin'):
        return self.app.open(url,
                             method=method,
                             headers={
                                      'Authorization': 'Basic ' + base64.b64encode(username +
                                                                                   ":" +
                                                                                   password)
                                      }
                             )
