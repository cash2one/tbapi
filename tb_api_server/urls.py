"""tb_api_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from api.views import *

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^get_store_info',get_store_info),
    url(r'^get_page_num',get_page_num),
    url(r'^get_products_info',get_products_info),
    url(r'^get_daren_prods',get_daren_prods),
]

'''
    test url:
        http://127.0.0.1:8000/get_store_info?store_url=https://detail.tmall.com/item.htm?id=538059530916&spm=a219t.7900221/10.1998910419.d30ccd691.YF4fJI
        http://127.0.0.1:8000/get_page_num?products_url=https://qyxcy.tmall.com/search.htm?search=y&orderType=newOn_desc&tsearch=y
        http://127.0.0.1:8000/get_products_info?products_url=https://qyxcy.tmall.com/search.htm?search=y&orderType=newOn_desc&tsearch=y
        http://127.0.0.1:8000/get_daren_prods?daren_url=http://ku.uz.taobao.com/
'''