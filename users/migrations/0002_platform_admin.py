from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="platform_admin",
            field=models.BooleanField(
                default=False,
                help_text="Can administer all tenants (ClinicCloud admin)",
            ),
        ),
    ]
