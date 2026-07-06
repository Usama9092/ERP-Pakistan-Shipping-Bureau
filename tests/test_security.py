import unittest

from modules.security import FileSecurityValidator, InputSanitizer, PasswordSecurity, SessionSecurity


class SecurityModuleTests(unittest.TestCase):
    def setUp(self):
        self.password_security = PasswordSecurity()
        self.session_security = SessionSecurity(secret="test-secret", timeout_minutes=5)
        self.sanitizer = InputSanitizer()
        self.file_validator = FileSecurityValidator(max_bytes=1024)

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

    def test_input_sanitizer_removes_script_and_controls(self):
        cleaned = self.sanitizer.sanitize_text("<script>alert(1)</script>\nHello\x00World")
        self.assertEqual(cleaned, "Hello World")

    def test_filename_sanitizer_blocks_path_traversal(self):
        safe_name = self.sanitizer.sanitize_filename("../../evil file.txt")
        self.assertEqual(safe_name, "evil-file.txt")

    def test_file_validator_rejects_oversized_uploads(self):
        valid, reason = self.file_validator.validate_upload("report.pdf", "application/pdf", 2048, {"pdf"})
        self.assertFalse(valid)
        self.assertIn("exceeds", reason)


if __name__ == "__main__":
    unittest.main()
