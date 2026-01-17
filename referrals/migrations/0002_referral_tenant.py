import django.db.models.deletion
from django.db import migrations, models


def set_referral_tenant(apps, schema_editor):
    Referral = apps.get_model("referrals", "Referral")
    for referral in Referral.objects.select_related("from_clinic__tenant").all():
        if (
            referral.tenant_id is None
            and referral.from_clinic
            and referral.from_clinic.tenant_id
        ):
            referral.tenant_id = referral.from_clinic.tenant_id
            referral.save(update_fields=["tenant"])


def unset_referral_tenant(apps, schema_editor):
    Referral = apps.get_model("referrals", "Referral")
    Referral.objects.update(tenant_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0003_tenant_specialization"),
        ("referrals", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="referral",
            name="tenant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="tenants.tenant",
            ),
        ),
        migrations.RunPython(set_referral_tenant, unset_referral_tenant),
        migrations.AlterField(
            model_name="referral",
            name="tenant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"
            ),
        ),
    ]
