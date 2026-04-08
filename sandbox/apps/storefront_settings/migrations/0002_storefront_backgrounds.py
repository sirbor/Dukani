# Generated manually for storefront background uploads

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storefront_settings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="storefrontbranding",
            name="nav_background",
            field=models.ImageField(
                blank=True,
                help_text="Optional. Banner behind the logo row in the header. Leave empty for the default bundled image.",
                upload_to="storefront/bg/",
                verbose_name="Main navigation bar background",
            ),
        ),
        migrations.AddField(
            model_name="storefrontbranding",
            name="book_room_background",
            field=models.ImageField(
                blank=True,
                help_text="Optional. Large home hero card for books. Leave empty for the default bookshelf photo.",
                upload_to="storefront/bg/",
                verbose_name='"The book room" hero tile',
            ),
        ),
        migrations.AddField(
            model_name="storefrontbranding",
            name="department_background_1",
            field=models.ImageField(
                blank=True,
                help_text="First department tile on the home page (left when four columns).",
                upload_to="storefront/bg/dept/",
                verbose_name="Browse by department — card 1",
            ),
        ),
        migrations.AddField(
            model_name="storefrontbranding",
            name="department_background_2",
            field=models.ImageField(
                blank=True,
                help_text="Second department tile.",
                upload_to="storefront/bg/dept/",
                verbose_name="Browse by department — card 2",
            ),
        ),
        migrations.AddField(
            model_name="storefrontbranding",
            name="department_background_3",
            field=models.ImageField(
                blank=True,
                help_text="Third department tile.",
                upload_to="storefront/bg/dept/",
                verbose_name="Browse by department — card 3",
            ),
        ),
        migrations.AddField(
            model_name="storefrontbranding",
            name="department_background_4",
            field=models.ImageField(
                blank=True,
                help_text="Fourth department tile.",
                upload_to="storefront/bg/dept/",
                verbose_name="Browse by department — card 4",
            ),
        ),
    ]
