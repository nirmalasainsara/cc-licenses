"""
Example deeds at

https://creativecommons.org/licenses/by/4.0/
https://creativecommons.org/licenses/by/4.0/deed.it
https://creativecommons.org/licenses/by-nc-sa/4.0/
https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es

"""

# Third-party
from django.urls import path, register_converter

# First-party/Local
from i18n import LANGUAGE_CODE_REGEX_STRING
from licenses import VERSION_REGEX_STRING
from licenses.views import view_deed, view_legal_code, view_metadata


class CategoryConverter:
    """
    Category must be either "licenses" or "publicdomain".
    """

    regex = r"licenses|publicdomain"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(CategoryConverter, "category")


class UnitConverter:
    """
    Units look like "MIT" or "by-sa" or "by-nc-nd" or "zero".
    We accept any mix of letters, digits, and dashes.
    """

    regex = r"(?i)[-a-z0-9+]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(UnitConverter, "unit")


class JurisdictionConverter:
    """
    jurisdiction should be ISO 3166-1 alpha-2 country code

    BUT it also looks as if we use "igo" and "scotland".
    """

    regex = r"[a-z]{2}|igo|scotland"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(JurisdictionConverter, "jurisdiction")


class VersionConverter:

    regex = VERSION_REGEX_STRING

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(VersionConverter, "version")


class LangConverter:
    """
    Django language code should be lowercase IETF language tag
    """

    regex = LANGUAGE_CODE_REGEX_STRING

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(LangConverter, "language_code")


# /licenses/
#       overview and links to the licenses (part of this project?)
# /licenses/?lang=es
#       overview and links to the licenses (part of this project?) in Spanish
#
# /licenses/by/4.0
#       deed for BY 4.0 English
# /licenses/by/4.0/deed.es
#       deed for BY 4.0 Spanish
# /licenses/by/4.0/legalcode
#       license BY 4.0 English
# /licenses/by/4.0/legalcode.es
#       license BY 4.0 Spanish
#
# /licenses/by/3.0/
#       deed for BY 3.0 Unported in English
# /licenses/by/3.0/legalcode
#       license for BY 3.0 Unported in English
#
# /licenses/by-nc-sa/3.0/de/
#       deed for by-nc-sa, 3.0, jurisdiction Germany, in German
# /licenses/by-nc-sa/3.0/de/deed.it
#       deed for by-nc-sa, 3.0, jurisdiction Germany, in Italian
# /licenses/by-nc-sa/3.0/de/legalcode
#       license for by-nc-sa, 3.0, jurisdiction Germany, in German
#       (I CANNOT find license for by-nc-sa 3.0 jurisdiction Germany in other
#       languages (/legalcode.it is a 404))
#
# /licenses/by-sa/2.5/ca/
#       deed for BY-SA 2.5, jurisdiction Canada, in English
# /licenses/by-sa/2.5/ca/deed.it
#       deed for BY-SA 2.5, jurisdiction Canada, in Italian
# /licenses/by-sa/2.5/ca/legalcode.en
#       license for BY-SA 2.5, jurisdiction Canada, in English
# /licenses/by-sa/2.5/ca/legalcode.fr
#       license for BY-SA 2.5, jurisdiction Canada, in French
#
# /licenses/by-sa/2.0/uk/
#       deed for BY-SA 2.0, jurisdiction England and Wales, in English
# /licenses/by-sa/2.0/uk/deed.es
#       deed for BY-SA 2.0, jurisdiction England and Wales, in Spanish
# /licenses/by-sa/2.0/uk/legalcode
#       license for BY-SA 2.0, jurisdiction England and Wales, in English


urlpatterns = [
    #
    # METADATA
    #
    path(
        "licenses/metadata.yaml",
        view_metadata,
        name="metadata",
    ),
    #
    # DEED PAGES
    #
    # Deed: with Jurisdiction (ported), with language_code
    path(
        "<category:category>/<unit:unit>/<version:version>"
        "/<jurisdiction:jurisdiction>/deed.<language_code:language_code>",
        view_deed,
        name="view_deed_ported_language_specified",
    ),
    # Deed: with Jurisdiction (ported), no language_code
    path(
        "<category:category>/<unit:unit>/<version:version>"
        "/<jurisdiction:jurisdiction>/deed",
        view_deed,
        name="view_deed_ported",
    ),
    # Deed: no Jurisdiction (international/unported), with language_code
    path(
        "<category:category>/<unit:unit>/<version:version>/deed"
        ".<language_code:language_code>",
        view_deed,
        kwargs=dict(jurisdiction=""),
        name="view_deed_unported_language_specified",
    ),
    # Deed: no Jurisdiction (international/unported), no language_code
    path(
        "<category:category>/<unit:unit>/<version:version>/deed",
        view_deed,
        kwargs=dict(jurisdiction=""),
        name="view_deed_unported",
    ),
    #
    # LEGALCODE PAGES
    #
    # Legalcode: with Jurisdiction (ported), with language_code
    path(
        "<category:category>/<unit:unit>/<version:version>"
        "/<jurisdiction:jurisdiction>/legalcode.<language_code:language_code>",
        view_legal_code,
        name="view_legal_code_ported_language_specified",
    ),
    # Legalcode: with Jurisdiction (ported), no language_code
    path(
        "<category:category>/<unit:unit>/<version:version>"
        "/<jurisdiction:jurisdiction>/legalcode",
        view_legal_code,
        name="view_legal_code_ported",
    ),
    # Legalcode: no Jurisdiction (international/unported), with language_code
    path(
        "<category:category>/<unit:unit>/<version:version>/legalcode"
        ".<language_code:language_code>",
        view_legal_code,
        kwargs=dict(jurisdiction=""),
        name="view_legal_code_unported_language_specified",
    ),
    # Legalcode: no Jurisdiction (international/unported), no language_code
    path(
        "<category:category>/<unit:unit>/<version:version>/legalcode",
        view_legal_code,
        kwargs=dict(jurisdiction=""),
        name="view_legal_code_unported",
    ),
    # NOTE: plaintext functionality disabled
    # # Plaintext Legalcode: no Jurisdiction (int/unported), no language_code
    # path(
    #     "<category:category>/<unit:unit>/<version:version>/legalcode.txt",
    #     view_legal_code,
    #     kwargs=dict(jurisdiction="", is_plain_text=True),
    #     name="view_legal_code_unported",
    # ),
]
