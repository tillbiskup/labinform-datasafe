import socket
import unittest

import datasafe.server as server


class TestBackend(unittest.TestCase):
    def setUp(self):
        self.backend = server.Backend()
        self.loi = '42.1001/ds/exp/sa/42/cwepr/1'

    def test_instantiate_class(self):
        pass

    def test_server_has_get_method(self):
        self.assertTrue(hasattr(self.backend, 'get'))
        self.assertTrue(callable(self.backend.get))
    
    def test_get_without_loi_raises(self):
        with self.assertRaises(server.MissingLoiError):
            self.backend.get()

    def test_get_with_loi(self):
        self.path = self.backend.get(self.loi)

    def test_get_with_invalid_loi_raises(self):
        with self.assertRaises(server.InvalidLoiError):
            self.backend.get('foo')

    def test_get_with_no_datasafe_loi_raises(self):
        with self.assertRaises(server.InvalidLoiError):
            self.backend.get('42.1001/rec/42')


class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = server.Server()

    def test_instantiate_class(self):
        pass

    def test_allows_connection(self):
        self.server.start()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('', 50000))


if __name__ == '__main__':
    unittest.main()
