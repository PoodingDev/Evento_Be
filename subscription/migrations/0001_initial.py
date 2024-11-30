import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("calendars", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "subscription_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                (
                    "calendar_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="calendars.calendar",
                    ),
                ),
            ],
        ),
    ]
