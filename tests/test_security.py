import unittest

from modules.security import PasswordSecurity, SessionSecurity


class SecurityModuleTests(unittest.TestCase):
    def setUp(self):
        self.password_security = PasswordSecurity()
        self.session_security = SessionSecurity(secret="test-secret", timeout_minutes=5)

    def test_password_hash_round_trip(self):
        password = "StrongP@ssw0rd!"
        hashed = self.password_security.hash_password(password)

        self.assertTrue(self.password_security.verify_password(password, hashed))
        self.assertFalse(self.password_security.verify_password("WrongPassword", hashed))

    def test_password_strength_policy(self):
        self.assertTrue(self.password_security.is_password_strong("StrongP@ssw0rd!"))
        self.assertFalse(self.password_security.is_password_strong("short"))
        self.assertFalse(self.password_security.is_password_strong("alllowercase123"))

    def test_session_token_validation_and_expiry(self):
        state = {}
        token = self.session_security.issue_session_token("user-1", "Admin", state)

        self.assertTrue(self.session_security.validate_session_token(state))
        self.assertEqual(state["auth_user_id"], "user-1")

        expired_state = {"auth_user_id": "user-1", "auth_session_token": token, "auth_expires_at": 0}
        self.assertFalse(self.session_security.validate_session_token(expired_state))


if __name__ == "__main__":
    unittest.main()
