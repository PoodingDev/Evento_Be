import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("event", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FavoriteEvent",
            fields=[
                (
                    "favorite_event_id",
                    models.BigAutoField(primary_key=True, serialize=False),
                ),
                ("d_day", models.DateField(auto_now_add=True)),
                ("easy_insidebar", models.BooleanField(default=False)),
                (
                    "event_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="event.event"
                    ),
                ),
            ],
        ),
    ]
