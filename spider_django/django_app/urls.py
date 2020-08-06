from django.conf.urls import url, include
from django_app import views

urlpatterns = [
    url(r'show_all_tasks$', views.show_all_tasks, ),
    url(r'show_all_confs$', views.show_all_confs, ),
    url(r'show_all_results$', views.show_all_results, ),
    url(r'add_tasks$', views.add_tasks, ),
    url(r'add_confs$', views.add_confs, ),
    url(r'add_results$', views.add_results, ),
    url(r'delete_tasks$', views.delete_tasks, ),
    url(r'delete_confs$', views.delete_confs, ),
    url(r'delete_results$', views.delete_results, ),
    url(r'modify_tasks$', views.modify_tasks, ),
    url(r'modify_confs$', views.modify_confs, ),
    url(r'modify_results$', views.modify_results, ),
    url(r'show_tasks$', views.show_tasks, ),
    url(r'show_confs$', views.show_confs, ),
    url(r'show_results$', views.show_results, ),
]