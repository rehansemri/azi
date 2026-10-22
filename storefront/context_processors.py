from .models import SiteSetting, PageContent, Color, Material, ConstructionType, ProductFeature, Size, MegaMenuItem, MegaMenuColumnConfig

def site_settings(request):
    try:
        settings_obj = SiteSetting.get_settings()
    except Exception:
        settings_obj = None

    pages_dict = {}
    try:
        for p in PageContent.objects.all():
            pages_dict[p.page_key] = p
    except Exception:
        pass

    # Dynamic navigation taxonomy fetched directly from Database Models
    try:
        nav_colors = list(Color.objects.all())
    except Exception:
        nav_colors = []

    try:
        nav_materials = list(Material.objects.all())
    except Exception:
        nav_materials = []

    try:
        nav_constructions = list(ConstructionType.objects.all())
    except Exception:
        nav_constructions = []

    try:
        nav_features = list(ProductFeature.objects.filter(is_highlighted=True).order_by('sort_order', 'name'))
    except Exception:
        nav_features = []

    try:
        nav_sizes = list(Size.objects.all().order_by('sort_order', 'id'))
    except Exception:
        nav_sizes = []

    # Mega Menu Custom Links from Database Model
    try:
        mega_featured_links = list(MegaMenuItem.objects.filter(section='featured', is_active=True).order_by('sort_order', 'id'))
        mega_custom_links = list(MegaMenuItem.objects.filter(section='custom', is_active=True).order_by('sort_order', 'id'))
        mega_one_of_a_kind_links = list(MegaMenuItem.objects.filter(section='one_of_a_kind', is_active=True).order_by('sort_order', 'id'))
    except Exception:
        mega_featured_links = []
        mega_custom_links = []
        mega_one_of_a_kind_links = []

    # Mega Menu Column Configurations (Titles, Visibility, Promo Banners)
    try:
        mega_cols = {col.column_key: col for col in MegaMenuColumnConfig.objects.all()}
    except Exception:
        mega_cols = {}

    return {
        'site_settings': settings_obj,
        'pages_content': pages_dict,
        'nav_colors': nav_colors,
        'nav_materials': nav_materials,
        'nav_constructions': nav_constructions,
        'nav_features': nav_features,
        'nav_sizes': nav_sizes,
        'mega_featured_links': mega_featured_links,
        'mega_custom_links': mega_custom_links,
        'mega_one_of_a_kind_links': mega_one_of_a_kind_links,
        'mega_cols': mega_cols,
    }



