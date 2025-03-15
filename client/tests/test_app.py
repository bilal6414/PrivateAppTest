import unittest
import cv2
from app import get_local_version

class TestApp(unittest.TestCase):
    def test_get_local_version(self):
        # Assuming version.txt contains "1.0.0" initially.
        version = get_local_version()
        self.assertEqual(version, "1.0.0", "Initial version should be 1.0.0")

    def test_opencv_version(self):
        cv_version = cv2.__version__
        self.assertTrue(isinstance(cv_version, str))
        self.assertNotEqual(cv_version, "")

if __name__ == "__main__":
    unittest.main()
