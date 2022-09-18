from .file_check import check_file_type
import unittest


class MyTestCase(unittest.TestCase):
    def test_errore(self):
        self.assertEqual("", check_file_type("testo.txt"))

    def test_immagine(self):
        self.assertEqual("image", check_file_type("immagine.jpeg"))

    def test_video(self):
        self.assertEqual("video", check_file_type("video.mp4"))


if __name__ == "__main__":
    unittest.main()
