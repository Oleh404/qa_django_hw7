from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("hello", "0001_initial"),
        # якщо у тебе є ще 0002..., тоді постав її сюди:
        # ("hello", "0002_alter_category_options_alter_subtask_options_and_more"),
    ]
    operations = [
        migrations.AlterModelTable(name="task", table="task_manager_task"),
        migrations.AlterModelTable(name="subtask", table="task_manager_subtask"),
        migrations.AlterModelTable(name="category", table="task_manager_category"),
    ]
