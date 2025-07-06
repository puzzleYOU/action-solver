from unittest import TestCase

from .presentation import Book, Locale


class DataLoaderUseCaseTest(TestCase):
    def test_full_fetch(self):
        self.assertEqual(
            Book(isbn="1337",
                 title="blubb",
                 locale=Locale(language_code="de", country_code="DE"),
                 authors=[],
                 previews=[],
                 ratings=[],
                 related_books=[]),
            None)

    def test_partial_fetch(self):
        self.fail()
