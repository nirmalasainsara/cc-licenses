# Generated by Django 2.2.20 on 2021-06-21 21:20

# Third-party
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LegalCode",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "language_code",
                    models.CharField(
                        help_text="E.g. 'en', 'en-ca', 'sr-Latn', or 'x-i18n'."
                        " Case-sensitive? This is the language code used by"
                        " CC, which might be a little different from the"
                        " Django language code.",
                        max_length=8,
                    ),
                ),
                (
                    "html_file",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="HTML file we got this from",
                        max_length=300,
                        verbose_name="HTML file",
                    ),
                ),
                (
                    "translation_last_update",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        default=None,
                        help_text="The last_updated field from Transifex for"
                        " this translation",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="License title in this language, e.g."
                        " 'Atribución/Reconocimiento 4.0 Internacional'",
                        max_length=112,
                    ),
                ),
                (
                    "html",
                    models.TextField(
                        blank=True, default="", verbose_name="HTML"
                    ),
                ),
                (
                    "license_url",
                    models.URLField(
                        blank=True, default="", verbose_name="License URL"
                    ),
                ),
                (
                    "deed_url",
                    models.URLField(unique=True, verbose_name="Deed URL"),
                ),
                (
                    "plain_text_url",
                    models.URLField(
                        blank=True, default="", verbose_name="Plain text URL"
                    ),
                ),
            ],
            options={
                "ordering": ["license", "language_code"],
            },
        ),
        migrations.CreateModel(
            name="TranslationBranch",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("branch_name", models.CharField(max_length=40)),
                (
                    "version",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="E.g. '4.0'. Not required.",
                        max_length=3,
                    ),
                ),
                (
                    "language_code",
                    models.CharField(
                        help_text="E.g. 'en', 'en-ca', 'sr-Latn', or 'x-i18n'."
                        " Case-sensitive? This is a CC language code,"
                        " which might differ from Django.",
                        max_length=8,
                    ),
                ),
                (
                    "last_transifex_update",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        default=None,
                        verbose_name="Time when last updated on Transifex.",
                    ),
                ),
                ("complete", models.BooleanField(default=False)),
                (
                    "legalcodes",
                    models.ManyToManyField(to="licenses.LegalCode"),
                ),
            ],
            options={
                "verbose_name_plural": "translation branches",
            },
        ),
        migrations.CreateModel(
            name="License",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "canonical_url",
                    models.URLField(
                        help_text="The license's unique identifier, e.g. "
                        "'https://creativecommons.org/licenses/by-nd/2.0/br/'",
                        unique=True,
                        verbose_name="Canonical URL",
                    ),
                ),
                (
                    "unit",
                    models.CharField(
                        help_text="shorthand representation for which class of"
                        " licenses this falls into. E.g. 'by-nc-sa', or 'MIT',"
                        " 'nc-sampling+', 'devnations', ...",
                        max_length=40,
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="E.g. '4.0'. Not required.",
                        max_length=3,
                    ),
                ),
                (
                    "jurisdiction_code",
                    models.CharField(blank=True, default="", max_length=9),
                ),
                (
                    "creator_url",
                    models.URLField(
                        blank=True,
                        default="",
                        help_text="E.g. https://creativecommons.org",
                        verbose_name="Creator URL",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="'licenses' or 'publicdomain'",
                        max_length=13,
                    ),
                ),
                (
                    "deprecated_on",
                    models.DateField(
                        null=True,
                        default=None,
                        help_text="if set, the date on which this license was"
                        " deprecated",
                    ),
                ),
                (
                    "permits_derivative_works",
                    models.BooleanField(default=None),
                ),
                ("permits_reproduction", models.BooleanField(default=None)),
                ("permits_distribution", models.BooleanField(default=None)),
                ("permits_sharing", models.BooleanField(default=None)),
                ("requires_share_alike", models.BooleanField(default=None)),
                ("requires_notice", models.BooleanField(default=None)),
                ("requires_attribution", models.BooleanField(default=None)),
                ("requires_source_code", models.BooleanField(default=None)),
                (
                    "prohibits_commercial_use",
                    models.BooleanField(default=None),
                ),
                (
                    "prohibits_high_income_nation_use",
                    models.BooleanField(default=None),
                ),
                (
                    "is_based_on",
                    models.ForeignKey(
                        help_text="another license that this one is based on",
                        blank=True,
                        null=True,
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="base_of",
                        to="licenses.License",
                    ),
                ),
                (
                    "is_replaced_by",
                    models.ForeignKey(
                        help_text="another license that has replaced this one",
                        blank=True,
                        null=True,
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replaces",
                        to="licenses.License",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        help_text="another license that this is the"
                        " translation of",
                        blank=True,
                        null=True,
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="source_of",
                        to="licenses.License",
                    ),
                ),
            ],
            options={
                "ordering": ["-version", "unit", "jurisdiction_code"],
            },
        ),
        migrations.AddField(
            model_name="legalcode",
            name="license",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="legal_codes",
                to="licenses.License",
            ),
        ),
    ]
