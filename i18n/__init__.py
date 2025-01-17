# Standard library
import logging
import os

# Third-party
from django.conf import settings

logger = logging.getLogger(__name__)

CSV_HEADERS = [
    "lang_ietf",
    "lang_locale",
    "num_messages",
    "num_trans",
    "num_fuzzy",
    "percent_trans",
]
DEFAULT_INPUT_DIR = os.path.dirname(settings.DEEDS_UX_LOCALE_PATH)
DEFAULT_CSV_FILE = os.path.abspath(
    os.path.realpath(os.path.join(settings.DISTILL_DIR, "transstats.csv"))
)
# The DEFAULT_JURISDICTION_LANGUAGES and JURISDICTION_NAMES are largely based
# on jurisdictions.rdf in the cc.licenserdf repo.
# The language codes here are CC language codes, which sometimes differ from
# Django language codes.
DEFAULT_JURISDICTION_LANGUAGES = {
    # Map jurisdiction code to language code.
    # "jurisdiction code": "Django language code"
    #
    # IMPORTANT: language codes and jurisdictions are different:
    # - jurisdictions are ISO 3166-1 alpha-2 codes
    # - Django language codes are lowercase IETF language tags:
    #
    # For example:
    # - "ar" is the ISO 3166-1 alpha-2 code for Argentina
    # - "ar" is the IETF language tag for Arabic
    #
    # See the "JURISDICTION_NAMES", just below this.
    "am": "hy",  # Armenian - not in jurisdictions.rdf
    "ar": "es",
    "at": "de",
    # jurisdictions.rdf says au is "en-gb", but:
    # Deed: https://creativecommons.org/licenses/by/3.0/au/
    # Deed: https://creativecommons.org/licenses/by/3.0/au/deed.en
    # https://creativecommons.org/licenses/by/3.0/au/deed.en-gb
    #   -> REDIRECTS to https://creativecommons.org/licenses/by/3.0/au/deed.en
    # Valid: https://creativecommons.org/licenses/by/3.0/au/legalcode
    # NOT: https://creativecommons.org/licenses/by/3.0/au/legalcode.en
    # NOT: https://creativecommons.org/licenses/by/3.0/au/legalcode.en-gb
    "au": "en",
    "az": "az",
    "be": "fr",
    "bg": "bg",
    "br": "pt-br",
    # For "ca", jurisdictions.rdf says "en-gb" but the filename is _en.html.
    # and the URL is
    # https://creativecommons.org/licenses/by/3.0/ca/legalcode.en
    # NOT https://creativecommons.org/licenses/by/3.0/ca
    # NOT https://creativecommons.org/licenses/by/3.0/ca/
    # NOT https://creativecommons.org/licenses/by/3.0/ca/legalcode.en-gb
    "ca": "en",
    # NOT https://creativecommons.org/licenses/by/3.0/ch/legalcode
    # YES https://creativecommons.org/licenses/by/3.0/ch/legalcode.de
    "ch": "de",  # ch=Switzerland, default in jurisdictions.rdf=de
    "cl": "es",
    "cn": "zh-hans",  # "cn" is China Mainland, language is simplified Chinese
    "co": "es",
    "cr": "es",
    "cz": "cs",
    "de": "de",
    "dk": "da",
    "ec": "es",
    "ee": "et",
    "eg": "ar",
    # For "es", jurisdictions.rdf says "es-es".
    # Deed https://creativecommons.org/licenses/by/3.0/es/ is valid
    # NOT https://creativecommons.org/licenses/by/3.0/es/legalcode
    # License https://creativecommons.org/licenses/by/3.0/es/legalcode.es is
    # valid
    # NOT https://creativecommons.org/licenses/by/3.0/es/legalcode.es-es
    # BUT the filename is by-nc-nd_3.0_es_es ????
    "es": "es",
    "fi": "fi",
    "fr": "fr",
    "ge": "ka",  # Georgia not in jurisdictions.rdf. Georgian?
    "gr": "el",
    "gt": "es",
    # Deed: https://creativecommons.org/licenses/by/3.0/hk/
    # License: https://creativecommons.org/licenses/by/3.0/hk/legalcode
    "hk": "en-gb",
    "hr": "hr",
    "hu": "hu",
    "ie": "en-gb",
    "igo": "en",
    "il": "he",
    "in": "en-gb",
    "it": "it",
    "jo": "ja",
    "jp": "ja",
    "kr": "ko",
    "lu": "fr",
    "mk": "mk",
    "mt": "en",
    "mx": "es",
    "my": "ms",
    "ng": "nl",
    "nl": "nl",
    "no": "no",
    "nz": "en",
    "pe": "es",
    "ph": "en",
    "pl": "pl",
    "pr": "es",
    "pt": "pt",
    "ro": "ro",
    "rs": "sr-latn",  # because "sr" Deed & UX translation is not complete
    "scotland": "en-gb",
    "se": "sv",
    "sg": "en-gb",
    "si": "sl",
    "th": "th",
    "tw": "zh-hant",
    "ua": "zh-hant",
    "ug": "en",
    "uk": "en-gb",
    "us": "en",
    "ve": "es",
    "vn": "vi",
    "za": "en-gb",
}
JURISDICTION_NAMES = {
    "": "Unported",
    "am": "Armenia",
    "ar": "Argentina",
    "at": "Austria",
    "au": "Australia",
    "az": "Azerbaijan",
    "be": "Belgium",
    "bg": "Bulgaria",
    "br": "Brazil",
    "ca": "Canada",
    "ch": "Switzerland",
    "cl": "Chile",
    "cn": "China Mainland",
    "co": "Colombia",
    "cr": "Costa Rica",
    "cz": "Czech Republic",
    "de": "Germany",
    "dk": "Denmark",
    "ec": "Ecuador",
    "ee": "Estonia",
    "eg": "Egypt",
    "es": "Spain",
    "fi": "Finland",
    "fr": "France",
    "ge": "Georgia",
    "gr": "Greece",
    "gt": "Guatemala",
    "hk": "Hong Kong",
    "hr": "Croatia",
    "hu": "Hungary",
    "ie": "Ireland",
    "igo": "IGO",
    "il": "Israel",
    "in": "India",
    "it": "Italy",
    "jo": "Jordan",
    "jp": "Japan",
    "kr": "Korea",
    "lu": "Luxembourg",
    "mk": "Macedonia",
    "mt": "Malta",
    "mx": "Mexico",
    "my": "Malaysia",
    "ng": "Nigeria",
    "nl": "Netherlands",
    "no": "Norway",
    "nz": "New Zealand",
    "pe": "Peru",
    "ph": "Philippines",
    "pl": "Poland",
    "pr": "Puerto Rico",
    "pt": "Portugal",
    "ro": "Romania",
    "rs": "Serbia",
    "scotland": "UK: Scotland",
    "se": "Sweden",
    "sg": "Singapore",
    "si": "Slovenia",
    "th": "Thailand",
    "tw": "Taiwan",
    "ua": "Ukraine",
    "ug": "Uganda",
    "uk": "UK: England & Wales",
    "us": "United States",
    "ve": "Venezuela",
    "vn": "Vietnam",
    "za": "South Africa",
}
LANGUAGE_CODE_REGEX_STRING = r"[a-z-]*"
LANGMAP_DJANGO_TO_REDIRECTS = {
    # Django language code: List of language codes that should redirect to it
    #
    # Django language codes are lowercase IETF language tags
    #
    # The map_django_to_redirects_language_codes function adds uppercase and
    # titlecase variants automatically (only lowercase language codes should be
    # added here).
    "de-at": ["de_at"],
    "en": ["en-us", "en_us"],
    "en-ca": ["en_ca"],
    "en-gb": ["en_gb"],
    "es": ["es-es", "es_es"],
    "es-ar": ["es_ar"],
    "es-pe": ["es_pe"],
    "fa-ir": ["fa_ir"],
    "fr-ca": ["fr_ca"],
    "fr-ch": ["fr_ch"],
    "oc-aranes": ["oci"],
    "pt-br": ["pt_br"],
    "si-lk": ["si_lk"],
    "sr": ["sr-cyrl", "sr@cyrl"],
    "sr-latn": ["sr-latin", "sr@latin"],
    "zh-hans": ["zh", "zh-cn", "zh_cn"],
    "zh-hant": ["zh-tw", "zh_tw"],
    "zh-hk": ["zh_hk"],
}
LANGMAP_DJANGO_TO_TRANSIFEX = {
    # Django language code: Transifex language code
    #
    # Django language codes are lowercase IETF language tags
    #
    # Transifex language codes are POSIX Locales
    #
    # Any changes here should also be made in .tx/config
    "de-at": "de_AT",
    "en-ca": "en_CA",
    "en-gb": "en_GB",
    "es-ar": "es_AR",
    "es-pe": "es_PE",
    "fa-ir": "fa_IR",
    "fr-ca": "fr_CA",
    "fr-ch": "fr_CH",
    "pt-br": "pt_BR",
    "si-lk": "si_LK",
    "sr-latn": "sr@latin",
    "zh-hans": "zh-Hans",
    "zh-hant": "zh-Hant",
    "zh-hk": "zh_HK",
}
LANGMAP_LEGACY_TO_DJANGO = {
    # Legacy language code: Django language code
    #
    # Note that Legacy language code is first transformed by
    # i18n.FUNCTION_NAME
    #
    # Legacy language codes include:
    # - POSIX Locales (ex. Transifex language codes)
    # - conventential IETF language tags (instead of lowercase, ex. zh-Hans)
    #
    # Django language codes are lowercase IETF language tags
    "en-us": "en",
    "es-es": "es",
    "oc": "oc-aranes",
    "oci": "oc-aranes",
    "oci-es": "oc-aranes",
    "oc@aranes": "oc-aranes",
    "sr-cyrl": "sr",
    "sr-latin": "sr-latn",
    "zh": "zh-hans",
    "zh-cn": "zh-hans",
    "zh-tw": "zh-hant",
}
