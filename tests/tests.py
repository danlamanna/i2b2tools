import unittest, sys, os
sys.path.insert(0, "../")

from i2b2tools.lib.standoff_annotations import StandoffAnnotation
from i2b2tools.lib.standoff_annotations.tags import Tag
from i2b2tools.lib.document_token import Document, Token

from i2b2tools.helpers.utils import is_valid_sa_file, get_sa_from_dir, has_overlapping_phi, phi_at_offset, phi_within_range
from i2b2tools.helpers.tokens import n_tokens, get_sa_tagged_tokens
from i2b2tools.helpers.mutable import sa_filter_by_phi_attrs

FIXTURES_PATH = "fixtures"

class TestIsValidSaFile(unittest.TestCase):
    def test_returns_false_with_nonexistent_file(self):
        self.assertFalse(is_valid_sa_file("nonexistent_file.jpeg"))

    def test_returns_true_with_valid_file(self):
        self.assertTrue(is_valid_sa_file(os.path.join(FIXTURES_PATH, "valid_sa_file1.xml")))

    def test_returns_false_with_invalid_files(self):
        self.assertFalse(is_valid_sa_file(os.path.join(FIXTURES_PATH, "invalid_sa_file1.xml")))
        self.assertFalse(is_valid_sa_file(os.path.join(FIXTURES_PATH, "invalid_sa_file2.xml")))
        self.assertFalse(is_valid_sa_file(os.path.join(FIXTURES_PATH, "invalid_sa_file3.xml")))

class TestGetSaFromDir(unittest.TestCase):
    def setUp(self):
        pass

    def test_only_valid_files_returned(self):
        self.assertDictEqual(get_sa_from_dir(os.path.join(FIXTURES_PATH, "empty_dir")), {})

        self.assertIsInstance(get_sa_from_dir(FIXTURES_PATH), dict)
        assert(len(get_sa_from_dir(FIXTURES_PATH).values()) == 4)

    def test_return_format(self):
        sas = get_sa_from_dir(FIXTURES_PATH)

        self.assertIsInstance(sas, dict)

        for (key, value) in sas.iteritems():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, StandoffAnnotation)

class TestHasOverlappingPhi(unittest.TestCase):
    def setUp(self):
        self.empty_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "valid_sa_file1.xml"))
        self.has_overlap_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "has_overlap1.xml"))
        self.no_overlap_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "no_overlap1.xml"))

    def test_raises_exception_for_non_standoff_annotations(self):
        self.assertRaises(Exception, has_overlapping_phi, "some string")

    def test_returns_true_for_overlapping_phi(self):
        self.assertTrue(has_overlapping_phi(self.has_overlap_sa))

    def test_returns_false_for_non_overlapping_phi(self):
        self.assertFalse(has_overlapping_phi(self.no_overlap_sa))
        self.assertFalse(has_overlapping_phi(self.empty_sa))

class TestPhiAtOffset(unittest.TestCase):
    def setUp(self):
        self.has_overlap_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "has_overlap1.xml"))

    def test_returns_nothing(self):
        self.assertEqual(phi_at_offset(self.has_overlap_sa, 1), [])

    def test_returns_multiple_phi_if_overlapping(self):
        assert(len(phi_at_offset(self.has_overlap_sa, 50)) == 2)

class TestPhiWithinRange(unittest.TestCase):
    def setUp(self):
        self.has_overlap_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "has_overlap1.xml"))

    def test_returns_all_phi_for_entire_document_range(self):
        all_phi_maybe = phi_within_range(self.has_overlap_sa, 0, len(self.has_overlap_sa.text))

        self.assertEqual(all_phi_maybe, self.has_overlap_sa.get_phi())


class TestNTokens(unittest.TestCase):
    def setUp(self):
        self.has_overlap_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "has_overlap1.xml"))
        self.document = Document(self.has_overlap_sa.file_name)

    def test_n_tokens(self):
        n = 3

        tokenset = n_tokens(self.document.token_sequence, n)

        for tokens in tokenset:
            assert(len(tokens) == n)

class TestGetSaTaggedTokens(unittest.TestCase):
    def setUp(self):
        self.has_overlap_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "has_overlap1.xml"))
        self.no_overlap_sa = StandoffAnnotation(os.path.join(FIXTURES_PATH, "no_overlap1.xml"))

    def test_raises_exception_for_non_standoff_annotations(self):
        self.assertRaises(Exception, get_sa_tagged_tokens, "a string")

    def test_raises_exception_for_overlapping_phi(self):
        self.assertRaises(Exception, get_sa_tagged_tokens, self.has_overlap_sa)

    def test_return_format(self):
        """
        This tests a few things:
        - get_sa_tagged_tokens always returns a list.
        - the list is a list of tuples with 2 elements
        - the first element is always of type Token, and the second is either None, or is of type Tag
        """
        tagged_tokens = get_sa_tagged_tokens(self.no_overlap_sa)

        self.assertIsInstance(tagged_tokens, list)

        for (token, associated_phi) in tagged_tokens:
            self.assertIsInstance(token, Token)
            assert(associated_phi is None or isinstance(associated_phi, Tag))

class TestSaFilterByPhiAttrs(unittest.TestCase):
    def setUp(self):
        self.sa1 = StandoffAnnotation(os.path.join(FIXTURES_PATH, "has_overlap1.xml"))

    def test_filtering(self):
        # No PHI will have an attribute of foo
        self.assertEqual(sa_filter_by_phi_attrs(self.sa1, {"foo": "bar"}), [])

        # No filters should be the same as all the PHI
        self.assertEqual(sa_filter_by_phi_attrs(self.sa1, {}), self.sa1.get_phi())

        # There should only be one PHI with the id P1.
        assert(len(sa_filter_by_phi_attrs(self.sa1, {"id": "P1"})) == 1)

if __name__ == "__main__":
    unittest.main()
