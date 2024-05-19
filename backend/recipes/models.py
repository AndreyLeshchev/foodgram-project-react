from colorfield.fields import ColorField

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField(
        max_length=250,
        verbose_name='Название',
        help_text='Введите название для тэга.',
        unique=True,
    )
    color = ColorField(
        max_length=7,
        verbose_name='Цвет',
        help_text='Введите цветовой код, например, #49B64E.',
        unique=True,
        default='#49B64E',
    )
    slug = models.CharField(
        max_length=250,
        verbose_name='Уникальное название',
        help_text='Введите уникальное название.',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Tэги'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'slug'),
                name='unique_name_slug',
            ),
        ]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        max_length=250,
        verbose_name='Ингредиент',
        help_text='Введите название для ингредиента.',
    )
    measurement_unit = models.CharField(
        max_length=250,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения для ингредиента.',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}.'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Выберите автора рецепта.',
    )
    name = models.CharField(
        max_length=250,
        verbose_name='Название рецепта',
        help_text='Введите название для рецепта.',
    )
    image = models.ImageField(
        upload_to='media/',
        blank=True,
        verbose_name='Фотография',
        help_text='Загрузите фотографию для рецепта.',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание для рецепта.',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты для рецепта.',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
        help_text='Выберите тэги для рецепта.',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message='Минимальное значение 1 в минутах.',
            ),
            MaxValueValidator(
                360, message='Минимальное значение 360 в минутах.',
            ),
        ],
        verbose_name='Время приготовления',
        help_text='Введите время для приготовления рецепта.',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_author_name',
            ),
        ]

    def __str__(self):
        return f'{self.name} - автор {self.author}.'


class RecipeIngredient(models.Model):
    """Вспомогательная модель для рецептов и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message='Минимальное значение ингредиента - 1.',
            ),
            MaxValueValidator(
                1000, message='Максимальное значение ингредиента - 1000.',
            ),
        ],
        verbose_name='Количество',
        help_text='Введите количество ингредиента.',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.recipe}: {self.ingredient}.'


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite_recipe_user',
            ),
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в избранное.'


class ShoppingCart(models.Model):
    """Модель для списка покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_shopping_recipe_user',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}.'
