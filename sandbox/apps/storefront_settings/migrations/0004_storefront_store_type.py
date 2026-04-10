# Generated manually: type of store (bookstore, etc.)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storefront_settings", "0003_storefront_hero_copy"),
    ]

    operations = [
        migrations.AddField(
            model_name="storefrontbranding",
            name="store_type",
            field=models.CharField(
                choices=[
                    ("bookstore", "Bookstore"),
                    ("general", "General retail"),
                    ("gift_shop", "Gift shop"),
                    ("specialty", "Specialty / other"),
                ],
                default="bookstore",
                help_text="Describes your shop (e.g. Bookstore). Used in the public layout where shown.",
                max_length=32,
                verbose_name="Type of store",
            ),
        ),
    ]
