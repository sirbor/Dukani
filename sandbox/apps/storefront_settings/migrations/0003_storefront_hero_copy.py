# Generated manually for homepage hero text fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storefront_settings", "0002_storefront_backgrounds"),
    ]

    operations = [
        migrations.AddField(
            model_name="storefrontbranding",
            name="home_hero_eyebrow",
            field=models.CharField(
                blank=True,
                help_text='e.g. “Est. 2024”. Leave blank for the default text.',
                max_length=160,
                verbose_name="Homepage hero — small line above the title",
            ),
        ),
        migrations.AddField(
            model_name="storefrontbranding",
            name="home_hero_title",
            field=models.CharField(
                blank=True,
                help_text="Usually your shop name. Leave blank to use the store name from settings.",
                max_length=255,
                verbose_name="Homepage hero — main headline",
            ),
        ),
        migrations.AddField(
            model_name="storefrontbranding",
            name="home_hero_lede",
            field=models.TextField(
                blank=True,
                help_text="One or two sentences under the headline. Leave blank for the default.",
                verbose_name="Homepage hero — supporting paragraph",
            ),
        ),
    ]
