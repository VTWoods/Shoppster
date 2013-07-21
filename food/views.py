# Create your views here.
from food.models import Recipe, ShopList, ShopAmount, Ingredient, IngredientForm
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.core.urlresolvers import reverse
from datetime import datetime
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.template import RequestContext

@login_required
def logout_view(request):
    logout(request)
    return redirect('food.views.index')

@login_required
def index(request):
    latest_recipe_list = Recipe.objects.filter(user=request.user).order_by('-add_date')[:5]
    latest_shop_list = ShopList.objects.filter(user=request.user).order_by('-add_date')[:5]
    return render_to_response('index.html', {'latest_recipe_list': latest_recipe_list,
                                             'latest_shop_list': latest_shop_list},
                              context_instance=RequestContext(request))
@login_required
def recipe_detail(request, recipe_id):
    try:
        r = Recipe.objects.get(pk=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404
    return render_to_response('recipeDetail.html', {'recipe': r},context_instance=RequestContext(request))

@login_required
def shop_list_detail(request, shop_list_id):
    
    try:
        shoplist = ShopList.objects.get(pk=shop_list_id)
        #Fix me (I shouldnt really redo this operation every time)
        if shoplist.dirty:
            shoplist.shopamount_set.all().delete()
            shoplist.consolidate_ingredients()
    except ShopList.DoesNotExist:
        raise Http404
    return render_to_response('shoplistDetail.html', {'shoplist':shoplist}, context_instance=RequestContext(request))

@login_required
def amount_toggle(request, amount_id):
    try:
        shop_amount = ShopAmount.objects.get(pk=amount_id)
        shop_amount.toggle_obtained()
        shop_amount.save()
    except ShopList.DoesNotExist:
        raise Http404
    
    return HttpResponse(content='')

@login_required
def ingredient_detail(request, ingr_id):
    i = Ingredient.objects.get(pk=ingr_id)
    form = IngredientForm(instance=i)
    return render_to_response('ingredientDetail.html', {'ingredient' : i, 'formset' : form}, context_instance=RequestContext(request))

def ingredient_update(request, ingr_id):
    if request.user.is_authenticated():
        return redirect("/food/")
    return HttpResponse(content='Error')
