import unittest
from flask import url_for
from Flask_app import app


class FlaskTestCase (unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config ['SERVER_NAME'] = 'localhost:5000'
        self.client = self.app.test_client ()
        self.ctx = self.app.app_context ()
        self.ctx.push ()

    def tearDown(self):
        self.ctx.pop ()

    def test_index(self):
        response = self.client.get (url_for ('index'))
        self.assertEqual (response.status_code, 200)

    def test_run_pathfinder(self):
        response = self.client.get (url_for ('run_pathfinder'))
        self.assertEqual (response.status_code, 200)
        self.assertEqual (response.mimetype, 'image/jpeg')
