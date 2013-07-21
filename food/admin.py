from food.models import *

from django.contrib import admin
from django import forms

class FoodAdminForm(forms.ModelForm):
    class Meta:
        model = Food

    def clean_name(self):
        return self.cleaned_data["name"].lower()

class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe

    def clean_name(self):
        return self.cleaned_data["name"].lower()

class FoodAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ]
    form = FoodAdminForm

class RecipeInline(admin.TabularInline):
    model = ShopListItem
    extra = 3
    form = RecipeAdminForm

class AmountInline(admin.TabularInline):
    model = ShopAmount

class UserTracked(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

class ShopListAdmin(UserTracked):
    list_display = ('name', 'add_date', 'user')
    list_filter = ['add_date']
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Date information', {'fields': ['add_date']}),
        ('Dirty State', {'fields': ['dirty']}),
    ]
    inlines = [RecipeInline]

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'add_date', 'user')
    list_filter = ['add_date']
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Date information', {'fields': ['add_date']}),
        ('User Name', {'fields': ['user']}),
    ]
    inlines = [IngredientInline]
    form = RecipeAdminForm

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShopList, ShopListAdmin)
admin.site.register(Food, FoodAdmin)
