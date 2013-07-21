from django.db import models, IntegrityError
from datetime import datetime
from fractions import Fraction
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class Recipe(models.Model):
    name = models.CharField(max_length=200, unique=True)
    add_date = models.DateTimeField('date added', default=datetime.now())
    user = models.ForeignKey(User)
    def __unicode__(self):
        return self.name.title()

class Food(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name.title()

class Countable(models.Model):
    numerator = models.IntegerField()
    denominator = models.IntegerField()
    measurement = models.CharField(max_length=50)
    food = models.ForeignKey(Food)

    class Meta:
        abstract = True

    def get_whole_number(self):
        return self.numerator / self.denominator

    def get_reduced_fraction(self):
        return Fraction(self.numerator - (self.get_whole_number() * self.denominator), self.denominator)

    def get_reduced_numerator(self):
        return self.get_reduced_fraction().numerator

    def get_reduced_denominator(self):
        return self.get_reduced_fraction().denominator

    def get_amount(self, frac_format):
        whole = self.get_whole_number()
        numer = self.get_reduced_numerator()
        denom = self.get_reduced_denominator()
        if (whole != 0 and (denom == 0 or numer == 0)):
            return "%d" % (whole)
        frac_string = frac_format % (numer, denom)
        if (whole == 0 and denom != 0):
            return frac_string
        else:
            return "%d %s" % (whole, frac_string)

    def get_amount_pretty(self):
        return self.get_amount("<sup>%d</sup>/<sub>%d</sub>")

    def get_amount_raw(self):
        return self.get_amount("%d/%d")

    def is_fraction(self):
        return (self.denominator != 1 or
                int(Fraction(self.numerator, self.denominator).denominator) != 1)

    def add_amount(self, add_ingredient):
        amount_frac = Fraction(self.numerator, self.denominator)
        new_frac = Fraction(add_ingredient.numerator,
                            add_ingredient.denominator)
        total_frac = amount_frac + new_frac
        self.numerator = total_frac.numerator
        self.denominator = total_frac.denominator

class Ingredient(Countable):
    recipe = models.ForeignKey(Recipe)

    def __unicode__(self):
        return "%s %s (%s)" % (self.get_amount_raw(), self.food, self.recipe.name)

class IngredientForm(ModelForm):
    class Meta:
        model = Ingredient
        fields = ('measurement',)

class ShopList(models.Model):
    name = models.CharField(max_length=200, default=datetime.now().strftime("%m/%d/%y %I:%M:%S %p"))
    add_date = models.DateTimeField('date added', default=datetime.now())
    cons_date = models.DateTimeField('date consolidated', default=datetime.now())
    dirty = models.BooleanField('needs cons', default=True)
    user = models.ForeignKey(User)
    
    def get_needed(self):
        return self.shopamount_set.all().filter(obtained=False)

    def get_obtained(self):
        return self.shopamount_set.all().filter(obtained=True)

    def consolidate_ingredients(self):
        shop_dict = {}
        for item in self.shoplistitem_set.all():
            for ingredient in item.recipe.ingredient_set.all():
                if ingredient.food.name in shop_dict:
                    shop_dict[ingredient.food.name].add_amount(ingredient)
                else:
                    shopamount = ShopAmount(food=ingredient.food,
                                            shoplist=self,
                                            numerator=ingredient.numerator,
                                            denominator=ingredient.denominator,
                                            measurement=ingredient.measurement)
                    shop_dict[ingredient.food.name] = shopamount
        self.cons_date = datetime.now()
        self.dirty = False
        self.save()
        for amount in shop_dict:
            shop_dict[amount].save()

    def __unicode__(self):
        return self.name

class ShopListItem(models.Model):
    recipe = models.ForeignKey(Recipe)
    shop_list = models.ForeignKey(ShopList)
 
class ShopAmount(Countable):
    shoplist = models.ForeignKey(ShopList)
    obtained = models.BooleanField(default=False)

    def toggle_obtained(self):
        self.obtained = not(self.obtained)
