# Standard library
from unittest import mock
from unittest.mock import MagicMock

# Third-party
import polib
from django.conf import settings
from django.test import TestCase, override_settings

# First-party/Local
from i18n.utils import (
    get_pofile_content,
    map_django_to_transifex_language_code,
)
from licenses.models import LegalCode
from licenses.tests.factories import LegalCodeFactory, LicenseFactory
from licenses.transifex import (
    LEGALCODES_KEY,
    TransifexHelper,
    _empty_branch_object,
)

TEST_PROJ_SLUG = "x_proj_x"
TEST_ORG_SLUG = "x_org_x"
TEST_TOKEN = "x_token_x"
TEST_TEAM_ID = "x_team_id_x"
TEST_TRANSIFEX_SETTINGS = {
    "ORGANIZATION_SLUG": TEST_ORG_SLUG,
    "PROJECT_SLUG": TEST_PROJ_SLUG,
    "API_TOKEN": TEST_TOKEN,
    "TEAM_ID": TEST_TEAM_ID,
}
POFILE_CONTENT = fr"""
msgid ""
msgstr ""
"Project-Id-Version: by-nd_40\n"
"Language-Team: https://www.transifex.com/{TEST_ORG_SLUG}/{TEST_PROJ_SLUG}/\n"
"Language: en\n"
"Language-Django: en\n"
"Language-Transifex: en\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "license_medium"
msgstr "Attribution-NoDerivatives 4.0 International"

msgid "english text"
msgstr "english text"
"""


# To shorten lines of code, make a short alias
# for  'mock.patch' and 'mock.patch.object'
mp = mock.patch
mpo = mock.patch.object


class DummyRepo:
    def __init__(self, path):
        self.index = MagicMock()
        self.remotes = MagicMock()
        self.branches = MagicMock()
        self.heads = MagicMock()

    # def __str__(self):
    #     return "a dummy repo"

    def __enter__(self):
        return self

    def __exit__(self, *a, **k):
        pass

    def is_dirty(self):
        return False

    def delete_head(self, name, force):
        pass


@override_settings(
    TRANSIFEX=TEST_TRANSIFEX_SETTINGS,
)
class TestTransifex(TestCase):
    def setUp(self):
        project_xa = mock.Mock(id="o:XA:p:XA", attributes={"slug": "XA"})
        project_xa.__str__ = mock.Mock(return_value=project_xa.id)
        project_xb = mock.Mock(id="o:XB:p:XB", attributes={"slug": "XB"})
        project_xb.__str__ = mock.Mock(return_value=project_xb.id)
        project_cc = mock.Mock(
            id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}",
            attributes={"slug": TEST_PROJ_SLUG},
        )
        project_cc.__str__ = mock.Mock(return_value=project_cc.id)
        project_xd = mock.Mock(id="o:XD:p:XD", attributes={"slug": "XD"})
        project_xd.__str__ = mock.Mock(return_value=project_xd.id)
        organization = mock.Mock(
            id=f"o:{TEST_ORG_SLUG}",
            attributes={"slug": TEST_ORG_SLUG},
        )
        organization.__str__ = mock.Mock(return_value=organization.id)
        organization.fetch = mock.Mock(
            return_value=[project_xa, project_xb, project_cc, project_xd]
        )
        i18n_format_xa = mock.Mock(id="XA")
        i18n_format_xa.__str__ = mock.Mock(return_value=i18n_format_xa.id)
        i18n_format_xb = mock.Mock(id="XB")
        i18n_format_xb.__str__ = mock.Mock(return_value=i18n_format_xb.id)
        i18n_format_po = mock.Mock(id="PO")
        i18n_format_po.__str__ = mock.Mock(return_value=i18n_format_po.id)
        i18n_format_xd = mock.Mock(id="XD")
        i18n_format_xd.__str__ = mock.Mock(return_value=i18n_format_xd.id)
        with mock.patch("licenses.transifex.transifex_api") as api:
            api.Organization.get = mock.Mock(return_value=organization)
            api.I18nFormat.filter = mock.Mock(
                return_value=[
                    i18n_format_xa,
                    i18n_format_xb,
                    i18n_format_po,
                    i18n_format_xd,
                ]
            )
            self.helper = TransifexHelper(dryrun=False)

        api.Organization.get.assert_called_once()
        organization.fetch.assert_called_once()
        api.I18nFormat.filter.assert_called_once()

    def test__empty_branch_object(self):
        empty = _empty_branch_object()
        self.assertEquals(empty, {LEGALCODES_KEY: []})

    def test_resource_stats(self):
        resources = [
            mock.Mock(
                id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:by-nc-nd_40",
                attributes={
                    "accept_translations": True,
                    "datetime_created": "2020-09-21T15:22:49Z",
                    "datetime_modified": "2020-10-05T13:23:22Z",
                    "i18n_type": "PO",
                    "i18n_version": 2,
                    "name": "CC BY-NC-ND 4.0",
                    "priority": "high",
                    "slug": "by-nc-nd_40",
                    "string_count": 74,
                    "word_count": 2038,
                },
            ),
            mock.Mock(
                id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:by-nc-sa_40",
                attributes={
                    "accept_translations": True,
                    "datetime_created": "2020-10-05T13:40:25Z",
                    "datetime_modified": "2020-10-05T13:40:25Z",
                    "i18n_type": "PO",
                    "i18n_version": 2,
                    "name": "CC BY-NC-SA 4.0",
                    "priority": "high",
                    "slug": "by-nc-sa_40",
                    "string_count": 84,
                    "word_count": 2289,
                },
            ),
        ]
        all_resources = mock.Mock(return_value=resources)
        self.helper.api_project.fetch = mock.Mock(
            return_value=mock.Mock(all=all_resources)
        )

        # With _resource_stats empty
        stats = self.helper.resource_stats
        # With _resource_stats populated
        stats = self.helper.resource_stats

        all_resources.assert_called_once()
        self.assertEqual(
            "2020-09-21T15:22:49Z", stats["by-nc-nd_40"]["datetime_created"]
        )
        self.assertEqual(2289, stats["by-nc-sa_40"]["word_count"])

    def test_translation_stats(self):
        languages_stats = [
            mock.Mock(
                id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:cc-search:l:es",
                attributes={
                    "last_proofread_update": None,
                    "last_review_update": "2018-04-15T12:50:40Z",
                    "last_translation_update": "2018-04-15T12:50:33Z",
                    "last_update": "2018-04-15T12:50:40Z",
                    "proofread_strings": 0,
                    "proofread_words": 0,
                    "reviewed_strings": 22,
                    "reviewed_words": 189,
                    "total_strings": 22,
                    "total_words": 189,
                    "translated_strings": 22,
                    "translated_words": 189,
                    "untranslated_strings": 0,
                    "untranslated_words": 0,
                },
                related={
                    "language": mock.Mock(id="l:es"),
                    "resource": mock.Mock(
                        id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:cc-search"
                    ),
                },
            ),
            mock.Mock(
                id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:deeds-choosers"
                ":l:nl",
                attributes={
                    "last_proofread_update": None,
                    "last_review_update": "2020-10-02T06:47:38Z",
                    "last_translation_update": "2020-10-02T06:47:38Z",
                    "last_update": "2020-10-02T06:47:38Z",
                    "proofread_strings": 0,
                    "proofread_words": 0,
                    "reviewed_strings": 572,
                    "reviewed_words": 8124,
                    "total_strings": 575,
                    "total_words": 8128,
                    "translated_strings": 575,
                    "translated_words": 8128,
                    "untranslated_strings": 0,
                    "untranslated_words": 0,
                },
                related={
                    "language": mock.Mock(id="l:nl"),
                    "resource": mock.Mock(
                        id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:"
                        "r:deeds-choosers"
                    ),
                },
            ),
            mock.Mock(
                id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:deeds_ux:l:id",
                attributes={
                    "last_proofread_update": None,
                    "last_review_update": None,
                    "last_translation_update": "2020-06-29T12:54:48Z",
                    "last_update": "2021-07-28T15:04:31Z",
                    "proofread_strings": 0,
                    "proofread_words": 0,
                    "reviewed_strings": 0,
                    "reviewed_words": 0,
                    "total_strings": 112,
                    "total_words": 2388,
                    "translated_strings": 0,
                    "translated_words": 0,
                    "untranslated_strings": 112,
                    "untranslated_words": 2388,
                },
                related={
                    "language": mock.Mock(id="l:id"),
                    "resource": mock.Mock(
                        id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:deeds_ux"
                    ),
                },
            ),
            mock.Mock(
                id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:deeds_ux:l:is",
                attributes={
                    "last_proofread_update": None,
                    "last_review_update": None,
                    "last_translation_update": "2020-09-18T09:46:58Z",
                    "last_update": "2021-07-28T15:04:31Z",
                    "proofread_strings": 0,
                    "proofread_words": 0,
                    "reviewed_strings": 0,
                    "reviewed_words": 0,
                    "total_strings": 112,
                    "total_words": 2388,
                    "translated_strings": 30,
                    "translated_words": 74,
                    "untranslated_strings": 82,
                    "untranslated_words": 2314,
                },
                related={
                    "language": mock.Mock(id="l:is"),
                    "resource": mock.Mock(
                        id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:deeds_ux"
                    ),
                },
            ),
            mock.Mock(
                id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:deeds_ux:l:it",
                attributes={
                    "last_proofread_update": None,
                    "last_review_update": None,
                    "last_translation_update": "2020-10-28T16:00:16Z",
                    "last_update": "2021-07-28T15:04:31Z",
                    "proofread_strings": 0,
                    "proofread_words": 0,
                    "reviewed_strings": 0,
                    "reviewed_words": 0,
                    "total_strings": 112,
                    "total_words": 2388,
                    "translated_strings": 50,
                    "translated_words": 500,
                    "untranslated_strings": 62,
                    "untranslated_words": 1888,
                },
                related={
                    "language": mock.Mock(id="l:it"),
                    "resource": mock.Mock(
                        id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:deeds_ux"
                    ),
                },
            ),
        ]
        all_lang_stats = mock.Mock(return_value=languages_stats)
        self.helper.api.ResourceLanguageStats.filter = mock.Mock(
            return_value=mock.Mock(all=all_lang_stats)
        )

        # With _resource_stats empty
        stats = self.helper.translation_stats
        # With _resource_stats populated
        stats = self.helper.translation_stats

        all_lang_stats.assert_called_once()
        self.assertNotIn("cc-search", stats)
        self.assertNotIn("deeds-choosers", stats)
        self.assertIn("deeds_ux", stats)
        self.assertIn("id", stats["deeds_ux"])
        self.assertIn("is", stats["deeds_ux"])
        self.assertIn("it", stats["deeds_ux"])
        self.assertEqual(
            0, stats["deeds_ux"]["id"].get("translated_strings", 0)
        )
        self.assertEqual(
            30, stats["deeds_ux"]["is"].get("translated_strings", 0)
        )
        self.assertEqual(
            50, stats["deeds_ux"]["it"].get("translated_strings", 0)
        )

    def test_transifex_get_pofile_content_bad_i18n_type(self):
        api = self.helper.api
        resource_slug = "x_resource_x"
        transifex_code = "en"
        resource = mock.Mock(
            id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:{resource_slug}",
            attributes={"i18n_type": "XA"},
        )
        self.helper.api.Resource.get = mock.Mock(return_value=resource)
        with mock.patch("requests.get") as request:
            with self.assertRaises(ValueError) as cm:
                self.helper.transifex_get_pofile_content(
                    resource_slug, transifex_code
                )

        self.assertEqual(
            f"Transifex {resource_slug} file format is not 'PO'. It is: XA",
            str(cm.exception),
        )
        api.ResourceStringsAsyncDownload.download.assert_not_called()
        api.ResourceTranslationsAsyncDownload.download.assert_not_called()
        request.assert_not_called()

    def test_transifex_get_pofile_content_source(self):
        api = self.helper.api
        resource_slug = "x_resource_x"
        transifex_code = "en"
        resource = mock.Mock(
            id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:{resource_slug}",
            attributes={"i18n_type": "PO"},
        )
        self.helper.api.Resource.get = mock.Mock(return_value=resource)
        with mock.patch("requests.get") as request:
            request.return_value = mock.MagicMock(content=b"xxxxxx")
            result = self.helper.transifex_get_pofile_content(
                resource_slug, transifex_code
            )

        api.ResourceStringsAsyncDownload.download.assert_called_once()
        api.ResourceTranslationsAsyncDownload.download.assert_not_called()
        self.assertEqual(result, b"xxxxxx")

    def test_transifex_get_pofile_content_translation(self):
        api = self.helper.api
        resource_slug = "x_resource_x"
        transifex_code = "nl"
        resource = mock.Mock(
            id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:{resource_slug}",
            attributes={"i18n_type": "PO"},
        )
        self.helper.api.Resource.get = mock.Mock(return_value=resource)
        with mock.patch("requests.get") as request:
            request.return_value = mock.MagicMock(content=b"yyyyyy")
            result = self.helper.transifex_get_pofile_content(
                resource_slug, transifex_code
            )

        api.ResourceStringsAsyncDownload.download.not_called()
        api.ResourceTranslationsAsyncDownload.download.assert_called_once()
        self.assertEqual(result, b"yyyyyy")

    def test_clear_transifex_stats(self):
        with self.assertRaises(AttributeError):
            self.helper._resource_stats
            self.helper._translation_stats

        self.helper.clear_transifex_stats()

        self.helper._resource_stats = 1
        self.helper._translation_stats = 1

        self.helper.clear_transifex_stats()

        with self.assertRaises(AttributeError):
            self.helper._resource_stats
            self.helper._translation_stats

    def test_build_local_data(self):
        license = LicenseFactory(unit="by", version="4.0")
        LegalCodeFactory(license=license, language_code=settings.LANGUAGE_CODE)
        LegalCodeFactory(license=license, language_code="de")
        legal_codes = LegalCode.objects.all()

        local_data = self.helper.build_local_data(legal_codes)

        self.assertEqual(local_data["deeds_ux"]["name"], "Deeds & UX")
        self.assertEqual(local_data["by_40"]["name"], "CC BY 4.0")
        self.assertEqual(
            list(local_data["by_40"]["translations"].keys()), ["de"]
        )

    # Test: add_resource_to_transifex ########################################

    def test_add_resource_to_transifex_present(self):
        language_code = "x_lang_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = "x_pofile_obj_x"
        # Set resource stats so we do not have to also mock it here
        self.helper._resource_stats = {"x_slug_x": None}

        self.helper.add_resource_to_transifex(
            language_code,
            resource_slug,
            resource_name,
            pofile_path,
            pofile_obj,
        )

        self.helper.api.Resource.create.assert_not_called()
        self.helper.api.Resource.get.assert_not_called()
        self.helper.api.ResourceStringsAsyncUpload.upload.assert_not_called()

    def test_add_resource_to_transifex_missing(self):
        language_code = "x_lang_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        resource = mock.Mock(
            id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:{resource_slug}",
            attributes={"i18n_type": "PO"},
        )
        self.helper.api.Resource.get = mock.Mock(return_value=resource)
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_content = get_pofile_content(pofile_obj)
        # Set resource stats so we do not have to also mock it here
        self.helper._resource_stats = {}

        self.helper.add_resource_to_transifex(
            language_code,
            resource_slug,
            resource_name,
            pofile_path,
            pofile_obj,
        )

        self.helper.api.Resource.create.assert_called_once()
        self.helper.api.Resource.create.assert_called_with(
            name=resource_name,
            slug=resource_slug,
            relationships={
                "i18n_format": self.helper.api_i18n_format,
                "project": self.helper.api_project,
            },
        )
        self.helper.api.Resource.get.assert_called_once()
        self.helper.api.ResourceStringsAsyncUpload.upload.assert_called_once()
        self.helper.api.ResourceStringsAsyncUpload.upload.assert_called_with(
            resource=resource,
            content=pofile_content.replace(
                'msgstr "english text"', 'msgstr ""'
            ),
        )

    def test_add_resource_to_transifex_dryrun(self):
        self.helper.dryrun = True
        language_code = "x_lang_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = "x_pofile_obj_x"
        # Set resource stats so we do not have to also mock it here
        self.helper._resource_stats = {}

        self.helper.add_resource_to_transifex(
            language_code,
            resource_slug,
            resource_name,
            pofile_path,
            pofile_obj,
        )

        self.helper.api.Resource.create.assert_not_called()
        self.helper.api.Resource.get.assert_not_called()
        self.helper.api.ResourceStringsAsyncUpload.upload.assert_not_called()

    # Test: add_translation_to_transifex_resource ############################

    def test_add_translation_to_transifex_resource_is_source(self):
        api = self.helper.api
        language_code = settings.LANGUAGE_CODE
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = "x_pofile_obj_x"
        # Set stats so we do not have to also mock them here
        self.helper._resource_stats = {}
        self.helper._translation_stats = {}

        with self.assertRaises(ValueError) as cm:
            self.helper.add_translation_to_transifex_resource(
                language_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        self.assertIn("x_name_x (x_slug_x) en", str(cm.exception))
        self.assertIn("is for translations, not sources.", str(cm.exception))
        api.Language.get.assert_not_called()
        api.Resource.get.assert_not_called()
        api.ResourceTranslationsAsyncUpload.upload.assert_not_called()

    def test_add_translation_to_transifex_resource_missing_source(self):
        api = self.helper.api
        language_code = "x_lang_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = "x_pofile_obj_x"
        # Set stats so we do not have to also mock them here
        self.helper._resource_stats = {}
        self.helper._translation_stats = {}

        with self.assertRaises(ValueError) as cm:
            self.helper.add_translation_to_transifex_resource(
                language_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        self.assertIn("x_name_x (x_slug_x) x_lang_code_x", str(cm.exception))
        self.assertIn(
            "Transifex does not yet contain resource.", str(cm.exception)
        )
        api.Language.get.assert_not_called()
        api.Resource.get.assert_not_called()
        api.ResourceTranslationsAsyncUpload.upload.assert_not_called()

    def test_add_translation_to_transifex_present(self):
        api = self.helper.api
        language_code = "x_lang_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        # Set resource stats so we do not have to also mock it here
        self.helper._resource_stats = {resource_slug: None}
        # Set translation stats so we do not have to also mock it here
        self.helper._translation_stats = {
            resource_slug: {language_code: {"translated_strings": 99}}
        }

        self.helper.add_translation_to_transifex_resource(
            language_code,
            resource_slug,
            resource_name,
            pofile_path,
            pofile_obj,
        )

        api.Language.get.assert_not_called()
        api.Resource.get.assert_not_called()
        api.ResourceTranslationsAsyncUpload.upload.assert_not_called()

    def test_add_translation_to_transifex_resource_dryrun(self):
        api = self.helper.api
        self.helper.dryrun = True
        language_code = "x_lang_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        # Set resource stats so we do not have to also mock it here
        self.helper._resource_stats = {resource_slug: None}
        # Set translation stats so we do not have to also mock it here
        self.helper._translation_stats = {resource_slug: {}}

        self.helper.add_translation_to_transifex_resource(
            language_code,
            resource_slug,
            resource_name,
            pofile_path,
            pofile_obj,
        )

        api.Language.get.assert_called_once()
        api.Resource.get.assert_called_once()
        api.ResourceTranslationsAsyncUpload.upload.assert_not_called()

    def test_add_translation_to_transifex_missing(self):
        api = self.helper.api
        language_code = "x_lang_code_x"
        transifex_code = map_django_to_transifex_language_code(language_code)
        language = mock.Mock(
            id=f"l:{transifex_code}",
        )
        self.helper.api.Language.get = mock.Mock(return_value=language)
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        resource = mock.Mock(
            id=f"o:{TEST_ORG_SLUG}:p:{TEST_PROJ_SLUG}:r:{resource_slug}",
            attributes={"i18n_type": "PO"},
        )
        self.helper.api.Resource.get = mock.Mock(return_value=resource)
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_content = get_pofile_content(pofile_obj)
        # Set resource stats so we do not have to also mock it here
        self.helper._resource_stats = {resource_slug: {}}
        # Set translation stats so we do not have to also mock it here
        self.helper._translation_stats = {resource_slug: {}}

        self.helper.add_translation_to_transifex_resource(
            language_code,
            resource_slug,
            resource_name,
            pofile_path,
            pofile_obj,
        )

        api.Language.get.assert_called_once()
        api.Resource.get.assert_called_once()
        api.ResourceTranslationsAsyncUpload.upload.assert_called_once()
        api.ResourceTranslationsAsyncUpload.upload.assert_called_with(
            resource=resource,
            content=pofile_content,
            language=language.id,
        )

    # Test: normalize_pofile_language ########################################

    def test_noramalize_pofile_language_correct(self):
        language_code = "en"
        transifex_code = "en"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_language(
                language_code,
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_noramalize_pofile_language_dryrun(self):
        self.helper.dryrun = True
        language_code = "en"
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_language(
                language_code,
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_noramalize_pofile_language_missing(self):
        language_code = "x_lang_code_x"
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata.pop("Language", None)
        pofile_obj.metadata.pop("Language-Django", None)
        pofile_obj.metadata.pop("Language-Transifex", None)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_language(
                language_code,
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_called()
        self.assertIn("Language", new_pofile_obj.metadata)
        self.assertEqual(new_pofile_obj.metadata["Language"], transifex_code)

    def test_noramalize_pofile_language_incorrect(self):
        language_code = "x_lang_code_x"
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_language(
                language_code,
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_called()
        self.assertEqual(new_pofile_obj.metadata["Language"], transifex_code)

    # Test: normalize_pofile_language_team ###################################

    def test_normalize_pofile_language_team_source_correct(self):
        transifex_code = "en"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_language_team(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_normalize_pofile_language_team_translation_correct(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata["Language-Team"] = (
            f"https://www.transifex.com/{TEST_ORG_SLUG}/teams/{TEST_TEAM_ID}"
            f"/{transifex_code}/"
        )

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_language_team(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_normalize_pofile_language_team_dryrun(self):
        self.helper.dryrun = True
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_language_team(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_normalize_pofile_language_team_incorrect(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_language_team(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_called()

    def test_normalize_pofile_language_team_missing(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata.pop("Language-Team", None)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_language_team(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_called()
        self.assertIn("Language-Team", new_pofile_obj.metadata)

    # Test: normalize_pofile_last_translator #################################

    def test_normalize_pofile_last_translator_missing(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata.pop("Last-Translator", None)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_last_translator(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()
        self.assertNotIn("Last-Translator", new_pofile_obj.metadata)

    def test_normalize_pofile_last_translator_correct(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata["Last-Translator"] = "valid_email@example.com"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_last_translator(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_normalize_pofile_last_translator_dryrun(self):
        self.helper.dryrun = True
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata["Last-Translator"] = "FULL NAME <EMAIL@ADDRESS>"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_last_translator(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_normalize_pofile_last_translator_incorrect(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata["Last-Translator"] = "FULL NAME <EMAIL@ADDRESS>"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_last_translator(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_called()
        self.assertNotIn("Last-Translator", new_pofile_obj.metadata)

    # Test: normalize_pofile_project_id ######################################

    def test_normalize_pofile_project_id_correct(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata["Project-Id-Version"] = resource_slug

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_project_id(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_normalize_pofile_project_id_dryrun(self):
        self.helper.dryrun = True
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata["Project-Id-Version"] = "PACKAGE VERSION"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.normalize_pofile_project_id(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()

    def test_normalize_pofile_project_id_incorrect(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata["Project-Id-Version"] = "PACKAGE VERSION"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_project_id(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_called()
        self.assertIn("Project-Id-Version", new_pofile_obj.metadata)
        self.assertEqual(
            resource_slug, new_pofile_obj.metadata["Project-Id-Version"]
        )

    def test_normalize_pofile_project_id_missing(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata.pop("Project-Id-Version", None)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_project_id(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_called()
        self.assertIn("Project-Id-Version", new_pofile_obj.metadata)
        self.assertEqual(
            resource_slug, new_pofile_obj.metadata["Project-Id-Version"]
        )

    # Test: normalize_pofile_metadata ########################################

    def test_normalize_pofile_metadata(self):
        self.helper.dryrun = True
        language_code = "x_lang_code_x"
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = self.helper.normalize_pofile_metadata(
                language_code,
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
            )

        mock_pofile_save.assert_not_called()
        self.assertEqual(pofile_obj, new_pofile_obj)

    # Test: update_pofile_creation_to_match_transifex ########################

    def test_update_pofile_creation_to_match_transifex_dryrun(self):
        self.helper.dryrun = True
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_creation = "2021-01-01 01:01:01+00:00"
        pofile_obj.metadata["POT-Creation-Date"] = pofile_creation
        transifex_creation = "2021-02-02 02:02:02+00:00"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.update_pofile_creation_to_match_transifex(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
                pofile_creation,
                transifex_creation,
            )

        mock_pofile_save.assert_not_called()

    def test_update_pofile_creation_to_match_transifex_save(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_creation = "2021-01-01 01:01:01+00:00"
        pofile_obj.metadata["POT-Creation-Date"] = pofile_creation
        transifex_creation = "2021-02-02 02:02:02+00:00"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = (
                self.helper.update_pofile_creation_to_match_transifex(
                    transifex_code,
                    resource_slug,
                    resource_name,
                    pofile_path,
                    pofile_obj,
                    pofile_creation,
                    transifex_creation,
                )
            )

        mock_pofile_save.assert_called()
        self.assertEqual(
            new_pofile_obj.metadata["POT-Creation-Date"], transifex_creation
        )

    # Test: update_pofile_revision_to_match_transifex ########################

    def test_update_pofile_revision_to_match_transifex_dryrun(self):
        self.helper.dryrun = True
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_revision = "2021-01-01 01:01:01+00:00"
        pofile_obj.metadata["PO-Revision-Date"] = pofile_revision
        transifex_revision = "2021-02-02 02:02:02+00:00"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            self.helper.update_pofile_revision_to_match_transifex(
                transifex_code,
                resource_slug,
                resource_name,
                pofile_path,
                pofile_obj,
                pofile_revision,
                transifex_revision,
            )

        mock_pofile_save.assert_not_called()

    def test_update_pofile_revision_to_match_transifex_save(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_revision = "2021-01-01 01:01:01+00:00"
        pofile_obj.metadata["PO-Revision-Date"] = pofile_revision
        transifex_revision = "2021-02-02 02:02:02+00:00"

        with mpo(polib.POFile, "save") as mock_pofile_save:
            new_pofile_obj = (
                self.helper.update_pofile_revision_to_match_transifex(
                    transifex_code,
                    resource_slug,
                    resource_name,
                    pofile_path,
                    pofile_obj,
                    pofile_revision,
                    transifex_revision,
                )
            )

        mock_pofile_save.assert_called()
        self.assertEqual(
            new_pofile_obj.metadata["PO-Revision-Date"], transifex_revision
        )

    # Test: normalize_pofile_dates ########################

    def test_normalize_pofile_dates_update_pofile_dates_missing(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        transifex_creation = "2021-01-01 01:01:01+00:00"
        transifex_revision = "2021-02-02 02:02:02+00:00"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_obj.metadata.pop("POT-Creation-Date", None)
        pofile_obj.metadata.pop("PO-Revision-Date", None)

        with mpo(
            self.helper, "get_transifex_resource_stats"
        ) as mock_resource_stats:
            mock_resource_stats.return_value = {
                resource_slug: {
                    "datetime_created": transifex_creation,
                    "datetime_modified": transifex_revision,
                },
            }
            with mpo(polib.POFile, "save") as mock_pofile_save:
                new_pofile_obj = self.helper.normalize_pofile_dates(
                    transifex_code,
                    resource_slug,
                    resource_name,
                    pofile_path,
                    pofile_obj,
                )

        mock_pofile_save.assert_called()
        self.assertEqual(
            new_pofile_obj.metadata["POT-Creation-Date"], transifex_creation
        )
        self.assertEqual(
            new_pofile_obj.metadata["PO-Revision-Date"], transifex_revision
        )

    def test_normalize_pofile_dates_update_pofile_creation_newer(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        transifex_creation = "2021-01-01 01:01:01+00:00"
        transifex_revision = "2021-02-02 02:02:02+00:00"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_creation = "2021-03-03 03:03:03+00:00"
        pofile_obj.metadata["POT-Creation-Date"] = pofile_creation
        pofile_obj.metadata["PO-Revision-Date"] = transifex_revision

        with mpo(
            self.helper, "get_transifex_resource_stats"
        ) as mock_resource_stats:
            mock_resource_stats.return_value = {
                resource_slug: {
                    "datetime_created": transifex_creation,
                    "datetime_modified": transifex_revision,
                },
            }
            with mpo(polib.POFile, "save") as mock_pofile_save:
                new_pofile_obj = self.helper.normalize_pofile_dates(
                    transifex_code,
                    resource_slug,
                    resource_name,
                    pofile_path,
                    pofile_obj,
                )

        mock_pofile_save.assert_called_once()
        self.assertEqual(
            new_pofile_obj.metadata["POT-Creation-Date"], transifex_creation
        )

    def test_normalize_pofile_dates_update_pofile_creation_older(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        transifex_creation = "2021-02-02 02:02:02+00:00"
        transifex_revision = "2021-03-03 03:03:03+00:00"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_creation = "2021-01-01 01:01:01+00:00"
        pofile_obj.metadata["POT-Creation-Date"] = pofile_creation
        pofile_obj.metadata["PO-Revision-Date"] = transifex_revision

        with self.assertLogs(self.helper.log) as log_context:
            with mpo(
                self.helper, "get_transifex_resource_stats"
            ) as mock_resource_stats:
                mock_resource_stats.return_value = {
                    resource_slug: {
                        "datetime_created": transifex_creation,
                        "datetime_modified": transifex_revision,
                    },
                }
                with mpo(polib.POFile, "save") as mock_pofile_save:
                    self.helper.normalize_pofile_dates(
                        transifex_code,
                        resource_slug,
                        resource_name,
                        pofile_path,
                        pofile_obj,
                    )

        mock_pofile_save.assert_not_called()
        self.assertTrue(log_context.output[0].startswith("ERROR:"))
        self.assertIn("'POT-Creation-Date' mismatch", log_context.output[0])

    def test_normalize_pofile_dates_update_pofile_entries_same(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        transifex_creation = "2021-01-01 01:01:01+00:00"
        transifex_revision = "2021-02-02 02:02:02+00:00"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(pofile=POFILE_CONTENT)
        pofile_revision = "2021-03-03 03:03:03+00:00"
        pofile_obj.metadata["POT-Creation-Date"] = transifex_creation
        pofile_obj.metadata["PO-Revision-Date"] = pofile_revision

        with mpo(
            self.helper, "transifex_get_pofile_content"
        ) as mock_transifex_content:
            mock_transifex_content.return_value = bytes(
                POFILE_CONTENT, "utf-8"
            )
            with mpo(
                self.helper, "get_transifex_resource_stats"
            ) as mock_resource_stats:
                mock_resource_stats.return_value = {
                    resource_slug: {
                        "datetime_created": transifex_creation,
                        "datetime_modified": transifex_revision,
                    },
                }
                with mpo(polib.POFile, "save") as mock_pofile_save:
                    new_pofile_obj = self.helper.normalize_pofile_dates(
                        transifex_code,
                        resource_slug,
                        resource_name,
                        pofile_path,
                        pofile_obj,
                    )

        mock_pofile_save.assert_called_once()
        self.assertEqual(
            new_pofile_obj.metadata["PO-Revision-Date"], transifex_revision
        )

    def test_normalize_pofile_dates_update_pofile_entries_different(self):
        transifex_code = "x_trans_code_x"
        resource_slug = "x_slug_x"
        resource_name = "x_name_x"
        transifex_creation = "2021-01-01 01:01:01+00:00"
        transifex_revision = "2021-02-02 02:02:02+00:00"
        pofile_path = "x_path_x"
        pofile_obj = polib.pofile(
            pofile=POFILE_CONTENT.replace("International", "Intergalactic")
        )
        pofile_revision = "2021-03-03 03:03:03+00:00"
        pofile_obj.metadata["POT-Creation-Date"] = transifex_creation
        pofile_obj.metadata["PO-Revision-Date"] = pofile_revision

        with self.assertLogs(self.helper.log) as log_context:
            with mpo(
                self.helper, "transifex_get_pofile_content"
            ) as mock_transifex_content:
                mock_transifex_content.return_value = bytes(
                    POFILE_CONTENT, "utf-8"
                )
                with mpo(
                    self.helper, "get_transifex_resource_stats"
                ) as mock_resource_stats:
                    mock_resource_stats.return_value = {
                        resource_slug: {
                            "datetime_created": transifex_creation,
                            "datetime_modified": transifex_revision,
                        },
                    }
                    with mpo(polib.POFile, "save") as mock_pofile_save:
                        self.helper.normalize_pofile_dates(
                            transifex_code,
                            resource_slug,
                            resource_name,
                            pofile_path,
                            pofile_obj,
                        )

        mock_pofile_save.assert_not_called()
        self.assertTrue(log_context.output[0].startswith("ERROR:"))
        self.assertIn("'PO-Revision-Date' mismatch", log_context.output[0])

    # def test_update_source_messages(self):
    #     with mpo(self.helper, "request20") as mock_request:
    #         self.helper.update_source_messages(
    #             "slug", "pofilename", "pofilecontent"
    #         )
    #     mock_request.assert_called_with(
    #         "put",
    #         "project/proj/resource/slug/content/",
    #         files=[
    #             (
    #                 "content",
    #                 (
    #                     "pofilename",
    #                     "pofilecontent",
    #                     "application/octet-stream",
    #                 ),
    #             )
    #         ],
    #     )

    # def test_update_translations(self):
    #     with mpo(self.helper, "request20") as mock_request:
    #         self.helper.update_translations(
    #             "slug", "lang", "pofilename", "pofilecontent"
    #         )
    #     mock_request.assert_called_with(
    #         "put",
    #         "project/proj/resource/slug/translation/lang/",
    #         files=[
    #             (
    #                 "file",
    #                 (
    #                     "pofilename",
    #                     "pofilecontent",
    #                     "application/octet-stream",
    #                 ),
    #             )
    #         ],
    #     )

    # def test_add_resource_to_transifex_no_resource_yet_not_english(self):
    #     # Must be english or we can't create the resource
    #     # If we try this with a non-english language and there's no resource,
    #     # we should get an error.
    #     legal_code = LegalCodeFactory(language_code="es")
    #     test_pofile = polib.POFile()
    #
    #     with mpo(self.helper, "get_transifex_resource_stats") as mock_gtr:
    #         mock_gtr.return_value = []
    #         with mpo(legal_code, "get_pofile") as mock_gpwem:
    #             mock_gpwem.return_value = test_pofile
    #             with self.assertRaisesMessage(
    #                 ValueError, "Must upload English first"
    #             ):
    #                 self.helper.add_resource_to_transifex(legal_code)
    #
    #     mock_gtr.assert_called_with()
    #     mock_gpwem.assert_called_with()

    # def test_upload_messages_english_resource_exists(self):
    #     # English because it's the source messages and is handled differently
    #     license = LicenseFactory(unit="by-nd", version="4.0")
    #     legal_code = LegalCodeFactory(
    #         license=license,
    #         language_code=settings.LANGUAGE_CODE,
    #     )
    #     test_resources = [
    #         {
    #             "slug": license.resource_slug,
    #         }
    #     ]
    #     test_pofile = polib.POFile()
    #     with mpo(self.helper, "get_transifex_resource_stats") as mock_gtr:
    #         mock_gtr.return_value = test_resources
    #         with mp("licenses.transifex.get_pofile_content") as mock_gpc:
    #             mock_gpc.return_value = "not really"
    #             with mpo(self.helper, "update_source_messages") as mock_usm:
    #                 self.helper.add_resource_to_transifex(
    #                     legal_code, test_pofile
    #                 )
    #
    #     mock_gtr.assert_called_with()
    #     mock_gpc.assert_called_with(test_pofile)
    #     mock_usm.assert_called_with(
    #         "by-nd_40",
    #         "/trans/repo/legalcode/en/LC_MESSAGES/by-nd_40.po",
    #         "not really",
    #     )

    # def test_upload_messages_non_english_resource_exists(self):
    #     # non-English because it's not the source messages and is handled
    #     # differently
    #     license = LicenseFactory(unit="by-nd", version="4.0")
    #     legal_code = LegalCodeFactory(license=license, language_code="fr")
    #     test_resources = [
    #         {
    #             "slug": license.resource_slug,
    #         }
    #     ]
    #     test_pofile = mock.MagicMock()
    #     with mpo(self.helper, "get_transifex_resource_stats") as mock_gtr:
    #         mock_gtr.return_value = test_resources
    #         with mp("licenses.transifex.get_pofile_content") as mock_gpc:
    #             mock_gpc.return_value = "not really"
    #             with mpo(self.helper, "update_translations") as mock_ut:
    #                 self.helper.add_resource_to_transifex(
    #                     legal_code, test_pofile
    #                 )
    #
    #     mock_gtr.assert_called_with()
    #     mock_gpc.assert_called_with(test_pofile)
    #     mock_ut.assert_called_with(
    #         "by-nd_40",
    #         "fr",
    #         "/trans/repo/legalcode/fr/LC_MESSAGES/by-nd_40.po",
    #         "not really",
    #     )

    # def test_get_transifex_resource_stats(self):
    #     # First call returns a response whose json value is a list of dicts
    #     # with slug keys
    #     call0_response = MagicMock()
    #     call0_response.json.return_value = [{"slug": "slug0"}]
    #
    #     # second call is more data about slug0 - FIXME
    #     call1_response = MagicMock()
    #     call1_response.json.return_value = {"stats": "stats1"}
    #     with mpo(self.helper, "request25") as mock_request25:
    #         # Return values for each call to request25
    #         mock_request25.side_effect = [
    #             call0_response,
    #             call1_response,
    #         ]
    #         result = self.helper.get_transifex_resource_stats()
    #     calls = mock_request25.call_args_list
    #     self.assertEqual(
    #         [
    #             call("get", "organizations/org/projects/proj/resources/"),
    #             call(
    #                 "get", "organizations/org/projects/proj/resources/slug0"
    #             ),
    #         ],
    #         calls,
    #     )
    #     self.assertEqual({"slug0": "stats1"}, result)


# @override_settings(
#     DATA_REPOSITORY_DIR="/trans/repo",
# )
# class CheckForTranslationUpdatesTest(TestCase):
#     def test_check_for_translation_updates_with_dirty_repo(self):
#         mock_repo = MagicMock()
#         mock_repo.__str__.return_value = "mock_repo"
#         mock_repo.is_dirty.return_value = True
#         with mock.patch.object(git, "Repo") as mock_Repo:
#             mock_Repo.return_value.__enter__.return_value = mock_repo
#             helper = TransifexHelper()
#             with self.assertRaisesMessage(
#                 Exception, "is dirty. We cannot continue."
#             ):
#                 helper.check_for_translation_updates()
#
#     def test_check_for_translation_updates_with_no_legal_codes(self):
#         mock_repo = MagicMock()
#         mock_repo.__str__.return_value = "mock_repo"
#         mock_repo.is_dirty.return_value = False
#         with mock.patch.object(git, "Repo") as mock_Repo:
#             mock_Repo.return_value.__enter__.return_value = mock_repo
#             with mock.patch.object(
#                 TransifexHelper, "get_transifex_resource_stats"
#             ) as mock_get_transifex_resource_stats:
#                 mock_get_transifex_resource_stats.return_value = {}
#                 helper = TransifexHelper()
#                 helper.check_for_translation_updates()
#
#     def test_check_for_translation_updates_first_time(self):
#         # We don't have a 'translation_last_update' yet to compare to.
#         self.help_test_check_for_translation_updates(
#             first_time=True, changed=None
#         )
#
#     def test_check_for_translation_updates_unchanged(self):
#         # The translation update timestamp has not changed
#         self.help_test_check_for_translation_updates(
#             first_time=False, changed=False
#         )
#
#     def test_check_for_translation_updates_changed(self):
#         # 'translation' is newer than translation_last_update
#         self.help_test_check_for_translation_updates(
#             first_time=False, changed=True
#         )
#
#     def test_check_for_translation_updates_add_resource_to_transifex(self):
#         # the resource isn't (yet) on transifex
#         self.help_test_check_for_translation_updates(
#             first_time=False, changed=True, resource_exists=False
#         )
#
#     def test_check_for_translation_updates_upload_language(self):
#         # The language isn't (yet) on transifex
#         self.help_test_check_for_translation_updates(
#             first_time=False, changed=True, language_exists=False
#         )
#
#     def help_test_check_for_translation_updates(
#         self, first_time, changed, resource_exists=True, language_exists=True
#     ):
#         """
#         Helper to test several conditions, since all the setup is so
#         convoluted.
#         """
#         language_code = "zh-Hans"
#         license = LicenseFactory(version="4.0", unit="by-nd")
#
#         first_translation_update_datetime = datetime.datetime(
#             2007, 1, 25, 12, 0, 0, tzinfo=utc
#         )
#         changed_translation_update_datetime = datetime.datetime(
#             2020, 9, 30, 13, 11, 52, tzinfo=utc
#         )
#
#         if first_time:
#             # We don't yet know when the last update was.
#             legal_code_last_update = None
#         else:
#             # The last update we know of was at this time.
#             legal_code_last_update = first_translation_update_datetime
#
#         legal_code = LegalCodeFactory(
#             license=license,
#             language_code=language_code,
#             translation_last_update=legal_code_last_update,
#         )
#         resource_slug = license.resource_slug
#
#         # Will need an English legal_code if we need to create the resource
#         if not resource_exists and language_code != settings.LANGUAGE_CODE:
#             LegalCodeFactory(
#                 license=license,
#                 language_code=settings.LANGUAGE_CODE,
#             )
#
#         # 'timestamp' returns on translation stats from transifex
#         if changed:
#             # now it's the newer time
#             timestamp = changed_translation_update_datetime.isoformat()
#         else:
#             # it's still the first time
#             timestamp = first_translation_update_datetime.isoformat()
#
#         mock_repo = MagicMock()
#         mock_repo.is_dirty.return_value = False
#
#         legal_codes = [legal_code]
#         dummy_repo = DummyRepo("/trans/repo")
#
#         # A couple of places use git.Repo(path) to get a git repo object.
#         # Have them all get back our same dummy repo.
#         def dummy_repo_factory(path):
#             return dummy_repo
#
#         helper = TransifexHelper()
#
#         with mpo(
#             helper, "handle_legal_codes_with_updated_translations"
#         ) as mock_handle_legal_codes, mpo(
#             helper, "get_transifex_resource_stats"
#         ) as mock_get_transifex_resource_stats, mpo(
#             helper, "add_resource_to_transifex"
#         ) as mock_add_resource_to_transifex, mpo(
#             LegalCode, "get_pofile"
#         ) as mock_get_pofile, mpo(
#             helper, "add_resource_to_transifex"
#         ) as mock_upload:
#             if resource_exists:
#                 if language_exists:
#                     mock_get_transifex_resource_stats.return_value = {
#                         resource_slug: {
#                             language_code: {
#                                 "translated": {
#                                     "last_activity": timestamp,
#                                 }
#                             }
#                         }
#                     }
#                 else:
#                     # language does not exist 1st time, does the 2nd time
#                     mock_get_transifex_resource_stats.side_effect = [
#                         {resource_slug: {}},
#                         {
#                             resource_slug: {
#                                 language_code: {
#                                     "translated": {
#                                         "last_activity": timestamp,
#                                     }
#                                 }
#                             }
#                         },
#                     ]
#             else:
#                 # First time does not exist, second time does
#                 mock_get_transifex_resource_stats.side_effect = [
#                     {},
#                     {
#                         resource_slug: {
#                             language_code: {
#                                 "translated": {
#                                     "last_activity": timestamp,
#                                 }
#                             }
#                         }
#                     },
#                 ]
#                 # Will need pofile
#                 mock_get_pofile.return_value = polib.POFile()
#             helper.check_for_translation_updates_with_repo_and_legal_codes(
#                 dummy_repo, legal_codes
#             )
#
#         if not resource_exists:
#             # Should have tried to create resource
#             mock_add_resource_to_transifex.assert_called_with(
#                 language_code=legal_code.language_code,
#                 resource_slug=resource_slug,
#                 resource_name=legal_code.license.identifier(),
#                 pofile_path=legal_code.translation_filename(),
#                 pofile_obj=mock_get_pofile,
#             )
#         else:
#             # Not
#             mock_add_resource_to_transifex.assert_not_called()
#
#         if language_exists:
#             mock_upload.assert_not_called()
#         else:
#             mock_upload.assert_called()
#
#         mock_get_transifex_resource_stats.assert_called_with()
#         legal_code.refresh_from_db()
#         if changed:
#             # we mocked the actual processing, so...
#             self.assertEqual(
#                 first_translation_update_datetime,
#                 legal_code.translation_last_update,
#             )
#             mock_handle_legal_codes.assert_called_with(
#                 dummy_repo, [legal_code]
#             )
#         else:
#             self.assertEqual(
#                 first_translation_update_datetime,
#                 legal_code.translation_last_update,
#             )
#             mock_handle_legal_codes.assert_called_with(dummy_repo, [])
#         return
#
#     def test_handle_legal_codes_with_updated_translations(self):
#         helper = TransifexHelper()
#         dummy_repo = DummyRepo("/trans/repo")
#
#         # No legal_codes, shouldn't call anything or return anything
#         result = helper.handle_legal_codes_with_updated_translations(
#             dummy_repo, []
#         )
#         self.assertEqual([], result)
#
#         # legal_codes for two branches
#         legal_code1 = LegalCodeFactory(
#             license__version="4.0",
#             license__unit="by-nc",
#             language_code="fr",
#         )
#         legal_code2 = LegalCodeFactory(
#             license__version="4.0",
#             license__unit="by-nd",
#             language_code="de",
#         )
#         with mpo(helper, "handle_updated_translation_branch") as mock_handle:
#             result = helper.handle_legal_codes_with_updated_translations(
#                 dummy_repo, [legal_code1, legal_code2]
#             )
#         self.assertEqual(
#             [legal_code1.branch_name(), legal_code2.branch_name()], result
#         )
#         self.assertEqual(
#             [
#                 mock.call(dummy_repo, [legal_code1]),
#                 mock.call(dummy_repo, [legal_code2]),
#             ],
#             mock_handle.call_args_list,
#         )
#
#     def test_handle_updated_translation_branch(self):
#         helper = TransifexHelper()
#         dummy_repo = DummyRepo("/trans/repo")
#         result = helper.handle_updated_translation_branch(dummy_repo, [])
#         self.assertIsNone(result)
#         legal_code1 = LegalCodeFactory(
#             license__version="4.0",
#             license__unit="by-nc",
#             language_code="fr",
#         )
#         legal_code2 = LegalCodeFactory(
#             license__version="4.0",
#             license__unit="by-nd",
#             language_code="fr",
#         )
#         with mp("licenses.transifex.setup_local_branch") as mock_setup, mpo(
#             helper, "update_branch_for_legal_code"
#         ) as mock_update_branch, mp(
#             "licenses.transifex.call_command"
#         ) as mock_call_command, mp(
#             "licenses.transifex.commit_and_push_changes"
#         ) as mock_commit:
#             # setup_local_branch
#             # update_branch_for_legal_code
#             # commit_and_push_changes
#             # branch_object.save()
#             result = helper.handle_updated_translation_branch(
#                 dummy_repo, [legal_code1, legal_code2]
#             )
#         self.assertIsNone(result)
#         mock_setup.assert_called_with(dummy_repo, legal_code1.branch_name())
#         # Should have published static files for this branch
#         expected = [
#             mock.call("publish", branch_name=legal_code1.branch_name()),
#         ]
#         self.assertEqual(expected, mock_call_command.call_args_list)
#         trb = TranslationBranch.objects.get()
#         expected = [
#             mock.call(dummy_repo, legal_code1, trb),
#             mock.call(dummy_repo, legal_code2, trb),
#         ]
#         self.assertEqual(expected, mock_update_branch.call_args_list)
#         mock_commit.assert_called_with(
#             dummy_repo, "Translation changes from Transifex.", "", push=True
#         )
#
#     def test_update_branch_for_legal_code(self):
#         helper = TransifexHelper()
#         dummy_repo = DummyRepo("/trans/repo")
#         legal_code = LegalCodeFactory(
#             license__version="4.0",
#             license__unit="by-nc",
#             language_code="fr",
#         )
#         helper._stats = {
#             legal_code.license.resource_slug: {
#                 legal_code.language_code: {
#                     "translated": {
#                         "last_activity": now().isoformat(),
#                     }
#                 }
#             }
#         }
#         trb = TranslationBranch.objects.create(
#             branch_name=legal_code.branch_name(),
#             version=legal_code.license.version,
#             language_code=legal_code.language_code,
#             complete=False,
#         )
#         content = b"wxyz"
#         # transifex_get_pofile_content
#         # save_content_as_pofile_and_mofile
#         with mpo(
#             helper, "transifex_get_pofile_content"
#         ) as mock_get_content, mp(
#             "licenses.transifex.save_content_as_pofile_and_mofile"
#         ) as mock_save:
#             mock_get_content.return_value = content
#             mock_save.return_value = [legal_code.translation_filename()]
#             result = helper.update_branch_for_legal_code(
#                 dummy_repo, legal_code, trb
#             )
#         self.assertIsNone(result)
#         mock_get_content.assert_called_with(
#             legal_code.license.resource_slug, legal_code.language_code
#         )
#         mock_save.assert_called_with(
#             legal_code.translation_filename(), content
#         )
#         self.assertEqual({legal_code}, set(trb.legal_codes.all()))
#         relpath = os.path.relpath(
#             legal_code.translation_filename(),
#             settings.DATA_REPOSITORY_DIR,
#         )
#         dummy_repo.index.add.assert_called_with([relpath])
#
