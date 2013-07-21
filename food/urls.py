from django.conf.urls import patterns, include, url

urlpatterns = patterns('food.views',
                       url(r'^$', 'index'),
                       url(r'^logout$','logout_view'),
                       url(r'^recipe/(?P<recipe_id>\d+)/$', 'recipe_detail'),
                       url(r'^shoplist/(?P<shop_list_id>\d+)/$', 'shop_list_detail'),
                       url(r'^ingredient/(?P<ingr_id>\d+)/update$', 'ingredient_update'),
                       url(r'^ingredient/(?P<ingr_id>\d+)/detail$', 'ingredient_detail'),
                       url(r'^amount/(?P<amount_id>\d+)/toggle$', 'amount_toggle'),
)
