# Generated by Django 3.2.16 on 2024-09-13 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20240912_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_shopping_cart', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]