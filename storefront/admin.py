from django.contrib import admin
from .models import (
    Category, Product, ProductVariant, ProductImage, RugCollection, Designer, Color, Size,
    ConstructionType, Material, Style, Shape, RoomType, SwatchSampleRequest, CustomerReview,
    ProjectList, ProjectListItem, CareGuide, TradeApplication, NewsletterSubscriber, SiteSetting, PageContent
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'catalog_code', 'collection', 'construction_type', 'primary_material', 'primary_color', 'price_from', 'is_in_stock', 'is_callaluxe', 'is_trending')
    list_filter = ('collection_obj', 'construction_type', 'primary_material', 'primary_color', 'traffic_rating', 'is_callaluxe', 'is_trending', 'is_in_stock')
    search_fields = ('name', 'catalog_code', 'collection')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('accent_colors', 'styles', 'rooms', 'shapes')
    inlines = [ProductImageInline, ProductVariantInline]

@admin.register(RugCollection)
class RugCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'designer', 'launch_season', 'is_featured')
    list_filter = ('is_featured', 'designer')
    search_fields = ('name', 'tagline')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Designer)
class DesignerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('name', 'bio')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_family', 'hex_code', 'is_primary')
    list_filter = ('color_family', 'is_primary')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('label', 'size_type', 'sqft', 'sort_order')
    list_filter = ('size_type',)
    search_fields = ('label',)
    prepopulated_fields = {'slug': ('label',)}

@admin.register(ConstructionType)
class ConstructionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'knot_count_typical', 'production_lead_weeks', 'heritage_region')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_natural', 'softness_score', 'durability_score', 'eco_certified')
    list_filter = ('is_natural', 'eco_certified')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'price', 'trade_price', 'sku', 'in_stock', 'inventory_count')
    list_filter = ('in_stock', 'is_swatch_sample')
    search_fields = ('sku', 'product__name', 'size')

@admin.register(SwatchSampleRequest)
class SwatchSampleRequestAdmin(admin.ModelAdmin):
    list_display = ('product', 'first_name', 'last_name', 'company', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('company', 'first_name', 'last_name', 'email', 'tracking_number')

@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'author_name', 'author_title', 'rating', 'is_verified_trade', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_trade', 'is_approved')
    search_fields = ('author_name', 'product__name', 'title')

class ProjectListItemInline(admin.TabularInline):
    model = ProjectListItem
    extra = 1

@admin.register(ProjectList)
class ProjectListAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer_name', 'designer_email', 'client_name', 'created_at')
    search_fields = ('title', 'designer_name', 'designer_email', 'client_name')
    inlines = [ProjectListItemInline]

@admin.register(CareGuide)
class CareGuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'material_target', 'slug')
    search_fields = ('title', 'material_target')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(TradeApplication)
class TradeApplicationAdmin(admin.ModelAdmin):
    list_display = ('company', 'first_name', 'last_name', 'email', 'business_type', 'created_at', 'approved')
    list_filter = ('approved', 'business_type')
    search_fields = ('company', 'first_name', 'last_name', 'email')

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated_at', 'announcement_active')

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page_key', 'title', 'updated_at')
