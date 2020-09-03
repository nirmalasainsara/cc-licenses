from unittest.mock import MagicMock

from bs4 import BeautifulSoup
from django.test import TestCase
from polib import POEntry

from licenses.utils import (
    get_code_from_jurisdiction_url,
    get_license_url_from_legalcode_url,
    parse_legalcode_filename,
    compute_about_url,
    validate_list_is_all_text,
    validate_dictionary_is_all_text,
    save_dict_to_pofile,
)


class GetJurisdictionCodeTest(TestCase):
    def test_get_code_from_jurisdiction_url(self):
        # Just returns the last portion of the path
        self.assertEqual(
            "foo", get_code_from_jurisdiction_url("http://example.com/bar/foo/")
        )
        self.assertEqual(
            "foo", get_code_from_jurisdiction_url("http://example.com/bar/foo")
        )
        self.assertEqual("", get_code_from_jurisdiction_url("http://example.com"))


class ParseLegalcodeFilenameTest(TestCase):
    # Test parse_legalcode_filename
    def test_parse_legalcode_filename(self):
        data = [
            (
                "by_1.0.html",
                {
                    "about_url": "http://creativecommons.org/licenses/by/1.0/",
                    "url": "http://creativecommons.org/licenses/by/1.0/",
                    "license_code": "by",
                    "version": "1.0",
                    "jurisdiction_code": "",
                    "language_code": "",
                },
            ),
            (
                "by_3.0_es_ast",
                {
                    "about_url": "http://creativecommons.org/licenses/by/3.0/es/",
                    "url": "http://creativecommons.org/licenses/by/3.0/es/legalcode.ast",
                    "license_code": "by",
                    "version": "3.0",
                    "jurisdiction_code": "es",
                    "language_code": "ast",
                },
            ),
            (
                "by_3.0_rs_sr-Cyrl.html",
                {
                    "about_url": "http://creativecommons.org/licenses/by/3.0/rs/",
                    "url": "http://creativecommons.org/licenses/by/3.0/rs/legalcode.sr-Cyrl",
                    "license_code": "by",
                    "version": "3.0",
                    "jurisdiction_code": "rs",
                    "language_code": "sr-Cyrl",
                },
            ),
            (
                "devnations_2.0.html",
                {
                    "about_url": "http://creativecommons.org/licenses/devnations/2.0/",
                    "url": "http://creativecommons.org/licenses/devnations/2.0/",
                    "license_code": "devnations",
                    "version": "2.0",
                    "jurisdiction_code": "",
                    "language_code": "",
                },
            ),
            (
                "LGPL_2.1.html",
                {
                    "about_url": "http://creativecommons.org/licenses/LGPL/2.1/",
                    "url": "http://creativecommons.org/licenses/LGPL/2.1/",
                    "license_code": "LGPL",
                    "version": "2.1",
                    "jurisdiction_code": "",
                    "language_code": "",
                },
            ),
            (
                "samplingplus_1.0",
                {
                    "about_url": "http://creativecommons.org/licenses/sampling+/1.0/",
                    "url": "http://creativecommons.org/licenses/sampling+/1.0/",
                    "license_code": "sampling+",
                    "version": "1.0",
                    "jurisdiction_code": "",
                    "language_code": "",
                },
            ),
            (
                "zero_1.0_fi.html",
                {
                    "about_url": "http://creativecommons.org/publicdomain/zero/1.0/",
                    "url": "http://creativecommons.org/publicdomain/zero/1.0/legalcode.fi",
                    "license_code": "CC0",
                    "version": "1.0",
                    "jurisdiction_code": "",
                    "language_code": "fi",
                },
            ),
            (
                "nc-samplingplus_1.0.html",
                {
                    "about_url": "http://creativecommons.org/licenses/nc-sampling+/1.0/",
                    "url": "http://creativecommons.org/licenses/nc-sampling+/1.0/",
                    "license_code": "nc-sampling+",
                    "version": "1.0",
                    "jurisdiction_code": "",
                    "language_code": "",
                },
            ),
        ]
        for filename, expected_result in data:
            with self.subTest(filename):
                result = parse_legalcode_filename(filename)
                if result != expected_result:
                    print(repr(result))
                self.assertEqual(expected_result, result)


class GetLicenseURLFromLegalCodeURLTest(TestCase):
    # get_license_url_from_legalcode_url
    def test_get_license_url_from_legalcode_url(self):
        data = [
            (
                "http://creativecommons.org/licenses/by/4.0/legalcode",
                "http://creativecommons.org/licenses/by/4.0/",
            ),
            (
                "http://creativecommons.org/licenses/by/4.0/legalcode.es",
                "http://creativecommons.org/licenses/by/4.0/",
            ),
            (
                "http://creativecommons.org/licenses/GPL/2.0/legalcode",
                "http://creativecommons.org/licenses/GPL/2.0/",
            ),
            (
                "http://creativecommons.org/licenses/nc-sampling+/1.0/tw/legalcode",
                "http://creativecommons.org/licenses/nc-sampling+/1.0/tw/",
            ),
            # Exceptions:
            (
                "http://opensource.org/licenses/bsd-license.php",
                "http://creativecommons.org/licenses/BSD/",
            ),
            (
                "http://opensource.org/licenses/mit-license.php",
                "http://creativecommons.org/licenses/MIT/",
            ),
        ]
        for legalcode_url, expected_license_url in data:
            with self.subTest(legalcode_url):
                self.assertEqual(
                    expected_license_url,
                    get_license_url_from_legalcode_url(legalcode_url),
                )
        with self.assertRaises(ValueError):
            get_license_url_from_legalcode_url(
                "http://opensource.org/licences/bsd-license.php"
            )


class TestComputeAboutURL(TestCase):
    def test_by_nc_40(self):
        self.assertEqual(
            "http://creativecommons.org/licenses/by-nc/4.0/",
            compute_about_url(
                license_code="by-nc", version="4.0", jurisdiction_code="",
            ),
        )

    def test_bsd(self):
        self.assertEqual(
            "http://creativecommons.org/licenses/BSD/",
            compute_about_url(license_code="BSD", version="", jurisdiction_code=""),
        )

    def test_mit(self):
        self.assertEqual(
            "http://creativecommons.org/licenses/MIT/",
            compute_about_url(license_code="MIT", version="", jurisdiction_code=""),
        )

    def test_gpl20(self):
        self.assertEqual(
            "http://creativecommons.org/licenses/GPL/2.0/",
            compute_about_url(license_code="GPL", version="2.0", jurisdiction_code=""),
        )

    def test_30_nl(self):
        self.assertEqual(
            "http://creativecommons.org/licenses/by/3.0/nl/",
            compute_about_url(
                license_code="by", version="3.0", jurisdiction_code="nl",
            ),
        )


class TestMisc(TestCase):
    def test_validate_list_is_all_text(self):
        validate_list_is_all_text(["a", "b"])
        with self.assertRaises(ValueError):
            validate_list_is_all_text(["a", 1])
        with self.assertRaises(ValueError):
            validate_list_is_all_text(["a", 4.2])
        with self.assertRaises(ValueError):
            validate_list_is_all_text(["a", object()])
        soup = BeautifulSoup("<span>foo</span>", "lxml")
        navstring = soup.span.string
        out = validate_list_is_all_text([navstring])
        self.assertEqual(["foo"], out)
        self.assertEqual([["foo"]], validate_list_is_all_text([[navstring]]))
        self.assertEqual([{"a": "foo"}], validate_list_is_all_text([{"a": navstring}]))

    def test_validate_dictionary_is_all_text(self):
        validate_dictionary_is_all_text({"1": "a", "2": "b"})
        with self.assertRaises(ValueError):
            validate_dictionary_is_all_text({"1": "a", "2": 1})
        with self.assertRaises(ValueError):
            validate_dictionary_is_all_text({"1": "a", "2": 3.14})
        with self.assertRaises(ValueError):
            validate_dictionary_is_all_text({"1": "a", "2": object()})
        soup = BeautifulSoup("<span>foo</span>", "lxml")
        navstring = soup.span.string
        self.assertEqual({"a": "foo"}, validate_dictionary_is_all_text({"a": navstring}))
        self.assertEqual({"a": ["foo"]}, validate_dictionary_is_all_text({"a": [navstring]}))
        self.assertEqual({"a": {"b": "foo"}}, validate_dictionary_is_all_text({"a": {"b": "foo"}}))

    def test_save_dict_to_pofile(self):
        mock_pofile = MagicMock()
        mock_pofile.append = MagicMock()
        messages = {"a": "one", "b": "two"}
        save_dict_to_pofile(mock_pofile, messages)
        self.assertEqual([], mock_pofile.call_args_list)
        self.assertEqual(2, len(mock_pofile.append.call_args_list))
        args, kwargs = mock_pofile.append.call_args_list[0]
        self.assertTrue(isinstance(args[0], POEntry))
