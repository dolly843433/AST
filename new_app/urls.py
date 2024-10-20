from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard_view,name='dashboard_view'),
    path('create', views.createRuleView, name='createRule'),
    path('combined', views.CombineRulesView, name='CombineRulesView'),
    path('evaluate_rule', views.evaluate_rule, name='evaluate_rule'),
    path('rules/', views.fetch_rules, name='fetch_rules'),  # New endpoint
]
