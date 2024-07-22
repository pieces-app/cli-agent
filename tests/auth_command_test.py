import unittest
from subprocess import run, PIPE

class TestAuthCommands(unittest.TestCase):
    def test_login_command(self):
        result = run(["poetry", "run", "pieces", "login"], stdout=PIPE, stderr=PIPE)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Logged in as", result.stdout.decode())

    def test_logout_command(self):
        result = run(["poetry", "run", "pieces", "logout"], stdout=PIPE, stderr=PIPE)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Logged out successfully", result.stdout.decode())

if __name__ == '__main__':
    unittest.main()
