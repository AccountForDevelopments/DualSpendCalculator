from django.apps import AppConfig


class CsvImportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "csv_import"
    verbose_name = "CSV取り込み"

