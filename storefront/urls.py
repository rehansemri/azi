from django.urls import path
from . import views
from . import dashboard_views

app_name = 'storefront'

urlpatterns = [
    path('', views.index, name='index'),
    path('rugs/', views.rugs_catalog, name='rugs'),
    path('rugs/new.html', views.rugs_new_catalog, name='rugs_new_html'),
    path('rugs/new/', views.rugs_new_catalog, name='rugs_new'),
    path('rugs/collections/<str:collection_slug>/', views.rugs_collection_catalog, name='rugs_collection'),
    path('rugs/collections/<str:collection_slug>.html', views.rugs_collection_catalog, name='rugs_collection_html'),
    path('decor/', views.decor_catalog, name='decor'),
    path('callaluxe/', views.callaluxe_page, name='callaluxe'),
    path('rugs/<slug:slug>/', views.product_detail, name='product_detail'),
    path('rugs/<slug:slug>.html', views.product_detail, name='product_detail_rugs_html'),
    path('<slug:slug>.html', views.product_detail, name='product_detail_direct_html'),
    path('the-jaipur-living-story/', views.story_page, name='story'),
    path('become-a-partner/', views.trade_page, name='trade'),
    path('contract/', views.contract_page, name='contract'),
    
    # Essential Pages (CMS Controllable)
    path('contact-us/', views.contact_page, name='contact'),
    path('customer-service/', views.customer_service_page, name='customer_service'),
    path('privacy-policy/', views.privacy_policy_page, name='privacy'),
    path('terms-and-conditions/', views.terms_conditions_page, name='terms'),
    path('refund-and-return-policy/', views.refund_policy_page, name='refund'),

    # APIs
    path('api/products/<int:product_id>/quick-view/', views.api_product_quick_view, name='api_quick_view'),
    path('api/cart/', views.api_cart, name='api_cart'),
    path('api/wishlist/toggle/', views.api_wishlist_toggle, name='api_wishlist_toggle'),
    path('api/trade/apply/', views.api_trade_apply, name='api_trade_apply'),
    path('api/newsletter/', views.api_newsletter, name='api_newsletter'),
    path('api/contact/', views.api_contact_submit, name='api_contact_submit'),

    # Power Admin Dashboard
    path('dashboard/', dashboard_views.dashboard_home, name='dashboard_home'),
    path('dashboard/login/', dashboard_views.dashboard_login, name='dashboard_login'),
    path('dashboard/quick-login/', dashboard_views.dashboard_quick_login, name='dashboard_quick_login'),
    path('dashboard/logout/', dashboard_views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/products/', dashboard_views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/new/', dashboard_views.dashboard_product_create, name='dashboard_product_create'),
    path('dashboard/products/<int:product_id>/edit/', dashboard_views.dashboard_product_edit, name='dashboard_product_edit'),
    path('dashboard/products/<int:product_id>/delete/', dashboard_views.dashboard_product_delete, name='dashboard_product_delete'),
    path('dashboard/products/<int:product_id>/variants/', dashboard_views.dashboard_product_variants, name='dashboard_product_variants'),
    path('dashboard/variants/new/', dashboard_views.dashboard_variant_create, name='dashboard_variant_create'),
    path('dashboard/variants/batch/', dashboard_views.dashboard_variants_batch_create, name='dashboard_variants_batch_create'),
    path('dashboard/variants/<int:variant_id>/delete/', dashboard_views.dashboard_variant_delete, name='dashboard_variant_delete'),
    path('dashboard/cms/', dashboard_views.dashboard_cms, name='dashboard_cms'),
    path('dashboard/media/', dashboard_views.dashboard_media_library, name='dashboard_media_library'),
    path('dashboard/media/upload/', dashboard_views.dashboard_media_upload, name='dashboard_media_upload'),
    path('dashboard/media/<int:asset_id>/delete/', dashboard_views.dashboard_media_delete, name='dashboard_media_delete'),
    path('dashboard/trade-applications/', dashboard_views.dashboard_trade_apps, name='dashboard_trade_apps'),
    path('dashboard/trade-applications/<int:app_id>/toggle/', dashboard_views.dashboard_trade_toggle_approve, name='dashboard_trade_toggle_approve'),
    path('dashboard/subscribers/', dashboard_views.dashboard_subscribers, name='dashboard_subscribers'),
    path('dashboard/swatches/', dashboard_views.dashboard_swatches, name='dashboard_swatches'),
    path('dashboard/swatches/<int:swatch_id>/status/', dashboard_views.dashboard_swatch_status, name='dashboard_swatch_status'),
    path('dashboard/reviews/', dashboard_views.dashboard_reviews, name='dashboard_reviews'),
    path('dashboard/reviews/<int:review_id>/toggle/', dashboard_views.dashboard_review_toggle, name='dashboard_review_toggle'),
    path('dashboard/inquiries/', dashboard_views.dashboard_inquiries, name='dashboard_inquiries'),
    path('dashboard/inquiries/<int:inquiry_id>/toggle/', dashboard_views.dashboard_inquiry_toggle, name='dashboard_inquiry_toggle'),
    # Taxonomy & Mega Menu
    path('dashboard/taxonomy/', dashboard_views.dashboard_taxonomy, name='dashboard_taxonomy'),
    path('dashboard/taxonomy/<str:entity_type>/add/', dashboard_views.dashboard_taxonomy_create, name='dashboard_taxonomy_create'),
    path('dashboard/taxonomy/<str:entity_type>/<int:item_id>/edit/', dashboard_views.dashboard_taxonomy_edit, name='dashboard_taxonomy_edit'),
    path('dashboard/taxonomy/<str:entity_type>/<int:item_id>/delete/', dashboard_views.dashboard_taxonomy_delete, name='dashboard_taxonomy_delete'),

    # Product Quick Actions & Bulk Controls
    path('dashboard/products/<int:product_id>/toggle-stock/', dashboard_views.dashboard_product_toggle_stock, name='dashboard_product_toggle_stock'),
    path('dashboard/products/<int:product_id>/toggle-trending/', dashboard_views.dashboard_product_toggle_trending, name='dashboard_product_toggle_trending'),
    path('dashboard/products/<int:product_id>/duplicate/', dashboard_views.dashboard_product_duplicate, name='dashboard_product_duplicate'),
    path('dashboard/products/bulk/', dashboard_views.dashboard_products_bulk_action, name='dashboard_products_bulk_action'),

    # Sitewide Global Settings
    path('dashboard/settings/', dashboard_views.dashboard_settings, name='dashboard_settings'),

    path('dashboard/tools/', dashboard_views.dashboard_db_tools, name='dashboard_db_tools'),
    path('dashboard/tools/export/', dashboard_views.dashboard_export_json, name='dashboard_export_json'),
    path('dashboard/tools/reseed/', dashboard_views.dashboard_reseed, name='dashboard_reseed'),
]
