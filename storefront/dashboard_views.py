import os
import uuid
import json
from decimal import Decimal
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q

from .models import (
    Category, Product, ProductVariant, ProductImage, TradeApplication, NewsletterSubscriber, SiteSetting, PageContent,
    RugCollection, Designer, Color, Size, ConstructionType, Material, Style, Shape, RoomType, ProductFeature,
    SwatchSampleRequest, CustomerReview, ProjectList, CareGuide, MediaAsset, ContactInquiry, MegaMenuItem, MegaMenuColumnConfig
)

def save_uploaded_media(file_obj, subfolder='uploads', title=None):
    """Save any uploaded media file (image, video, 3D model, document, etc.) to media directory,
    automatically catalog into MediaAsset library, and return public URL."""
    if not file_obj:
        return ''
    dest_dir = os.path.join(settings.MEDIA_ROOT, subfolder)
    os.makedirs(dest_dir, exist_ok=True)
    clean_name = file_obj.name.replace(' ', '_')
    filename = f"{uuid.uuid4().hex[:8]}_{clean_name}"
    saved_path = default_storage.save(f'{subfolder}/{filename}', file_obj)
    file_url = f'{settings.MEDIA_URL}{saved_path}'

    # Auto-detect media type
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.avif']:
        ftype = 'image'
    elif ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v']:
        ftype = 'video'
    elif ext in ['.usdz', '.glb', '.gltf', '.obj']:
        ftype = 'model3d'
    elif ext in ['.pdf', '.doc', '.docx', '.csv', '.xlsx', '.txt']:
        ftype = 'document'
    else:
        ftype = 'other'

    fsize = getattr(file_obj, 'size', 0)
    fmime = getattr(file_obj, 'content_type', '')

    try:
        MediaAsset.objects.create(
            title=title or file_obj.name,
            file_name=file_obj.name,
            file_url=file_url,
            file_size=fsize,
            file_type=ftype,
            mime_type=fmime,
        )
    except Exception:
        pass

    return file_url

def check_admin_auth(request):
    """Check if current user is logged in as staff, or session has demo admin flag."""
    return request.user.is_authenticated and request.user.is_staff or request.session.get('demo_admin_logged_in', False)

def dashboard_home(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    total_products = Product.objects.count()
    total_variants = ProductVariant.objects.count()
    total_trade_apps = TradeApplication.objects.count()
    pending_trade_apps = TradeApplication.objects.filter(approved=False).count()
    total_subscribers = NewsletterSubscriber.objects.count()
    total_inquiries = ContactInquiry.objects.count()
    pending_inquiries = ContactInquiry.objects.filter(is_resolved=False).count()
    collections_count = Product.objects.values('collection').distinct().count()
    in_stock_count = Product.objects.filter(is_in_stock=True).count()
    in_stock_pct = int(round((in_stock_count / total_products * 100))) if total_products > 0 else 0

    recent_products = Product.objects.order_by('-id')[:6]
    recent_trade_apps = TradeApplication.objects.order_by('-id')[:5]
    recent_inquiries = ContactInquiry.objects.order_by('-id')[:5]
    site_settings = SiteSetting.get_settings()

    context = {
        'active_tab': 'overview',
        'total_products': total_products,
        'total_variants': total_variants,
        'total_trade_apps': total_trade_apps,
        'pending_trade_apps': pending_trade_apps,
        'total_inquiries': total_inquiries,
        'pending_inquiries': pending_inquiries,
        'recent_inquiries': recent_inquiries,
        'total_subscribers': total_subscribers,
        'collections_count': collections_count,
        'in_stock_pct': in_stock_pct,
        'recent_products': recent_products,
        'recent_trade_apps': recent_trade_apps,
        'site_settings': site_settings,
    }
    return render(request, 'storefront/dashboard/index.html', context)

def dashboard_products(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    products = Product.objects.prefetch_related('variants', 'category').order_by('-id')
    categories = Category.objects.all()

    # Search & filters
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(name__icontains=q) | products.filter(catalog_code__icontains=q) | products.filter(collection__icontains=q)
    
    col_filter = request.GET.get('collection', '').strip()
    if col_filter:
        products = products.filter(collection__iexact=col_filter)

    collections_list = Product.objects.values_list('collection', flat=True).distinct()

    context = {
        'active_tab': 'products',
        'products': products,
        'categories': categories,
        'collections_list': collections_list,
        'search_query': q,
        'selected_collection': col_filter,
    }
    return render(request, 'storefront/dashboard/products.html', context)

def get_taxonomy_context():
    return {
        'categories': Category.objects.all(),
        'collections': RugCollection.objects.all(),
        'designers': Designer.objects.all(),
        'colors': Color.objects.all(),
        'materials': Material.objects.all(),
        'constructions': ConstructionType.objects.all(),
        'styles': Style.objects.all(),
        'shapes': Shape.objects.all(),
        'rooms': RoomType.objects.all(),
        'features': ProductFeature.objects.all(),
        'traffic_choices': Product.TRAFFIC_CHOICES,
    }

DEFAULT_ARTISAN_STORY = (
    "Handcrafted by generational master weavers in Rajasthan, India, this heirloom-quality rug unites "
    "centuries-old knotting artistry with contemporary interior elegance. Spun from pure natural fibers "
    "with meticulous knot-by-knot precision, each piece embodies the dedication, soulful craft, and human "
    "touch of over 40,000 artisan families."
)
DEFAULT_CARE_INSTRUCTIONS = (
    "Vacuum regularly on low-power suction-only setting without a rotating beater bar. Spot clean spills "
    "immediately by blotting with a clean, undyed cloth and mild pH-neutral soap. Professional hand immersion "
    "rug cleaning recommended every 3-5 years. Rug pad recommended to prevent slipping and extend fiber longevity."
)

@require_http_methods(["GET", "POST"])
def dashboard_product_create(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        catalog_code = request.POST.get('catalog_code', '').strip().upper()
        collection = request.POST.get('collection', '').strip()
        category_id = request.POST.get('category')
        construction = request.POST.get('construction', 'Hand Knotted')
        material = request.POST.get('material', '100% Wool')
        origin = request.POST.get('origin', 'Rajasthan, India')
        pile_height = request.POST.get('pile_height', '1/2"')
        price_from = Decimal(request.POST.get('price_from', '1250.00'))
        badge = request.POST.get('badge', '').strip()
        description = request.POST.get('description', '').strip() or DEFAULT_ARTISAN_STORY
        care_instructions = request.POST.get('care_instructions', '').strip() or DEFAULT_CARE_INSTRUCTIONS
        
        # Support file uploads with fallback to text URL
        if request.FILES.get('image_file'):
            image_url = save_uploaded_media(request.FILES.get('image_file'), 'products', title=f"{name} Primary Shot")
        else:
            image_url = request.POST.get('image_url', '').strip()

        if request.FILES.get('secondary_image_file'):
            secondary_image_url = save_uploaded_media(request.FILES.get('secondary_image_file'), 'products', title=f"{name} Texture Close-Up")
        else:
            secondary_image_url = request.POST.get('secondary_image_url', '').strip()

        if request.FILES.get('lifestyle_image_file'):
            lifestyle_image_url = save_uploaded_media(request.FILES.get('lifestyle_image_file'), 'products', title=f"{name} Lifestyle")
        else:
            lifestyle_image_url = request.POST.get('lifestyle_image_url', '').strip()

        # Video file upload or URL
        if request.FILES.get('video_file'):
            video_url = save_uploaded_media(request.FILES.get('video_file'), 'videos', title=f"{name} Video Feature")
        else:
            video_url = request.POST.get('video_url', '').strip()

        # 3D AR Model file upload or URL
        if request.FILES.get('ar_model_file'):
            ar_model_url = save_uploaded_media(request.FILES.get('ar_model_file'), 'models3d', title=f"{name} 3D AR Model")
        else:
            ar_model_url = request.POST.get('ar_model_url', '').strip()

        is_trending = request.POST.get('is_trending') == 'on'
        is_callaluxe = request.POST.get('is_callaluxe') == 'on'
        is_in_stock = request.POST.get('is_in_stock') == 'on'

        cat = get_object_or_404(Category, id=category_id) if category_id else Category.objects.first()

        # Advanced entities
        collection_obj_id = request.POST.get('collection_obj')
        designer_id = request.POST.get('designer')
        primary_material_id = request.POST.get('primary_material')
        construction_type_id = request.POST.get('construction_type')
        primary_color_id = request.POST.get('primary_color')

        product = Product.objects.create(
            name=name,
            catalog_code=catalog_code,
            collection=collection,
            category=cat,
            construction=construction,
            material=material,
            origin=origin,
            pile_height=pile_height,
            price_from=price_from,
            badge=badge,
            description=description,
            care_instructions=care_instructions,
            image_url=image_url,
            secondary_image_url=secondary_image_url,
            lifestyle_image_url=lifestyle_image_url,
            is_trending=is_trending,
            is_callaluxe=is_callaluxe,
            is_in_stock=is_in_stock,
            collection_obj_id=collection_obj_id if collection_obj_id else None,
            designer_id=designer_id if designer_id else None,
            primary_material_id=primary_material_id if primary_material_id else None,
            construction_type_id=construction_type_id if construction_type_id else None,
            primary_color_id=primary_color_id if primary_color_id else None,
            knot_count=request.POST.get('knot_count', '80-120 KPSI').strip(),
            traffic_rating=request.POST.get('traffic_rating', 'High'),
            backing=request.POST.get('backing', 'Cotton Weft / Canvas').strip(),
            video_url=video_url,
            ar_model_url=ar_model_url,
            is_outdoor_safe=request.POST.get('is_outdoor_safe') == 'on',
            is_floor_heating_safe=request.POST.get('is_floor_heating_safe') == 'on',
            is_custom_size_available=request.POST.get('is_custom_size_available') == 'on',
            sample_available=request.POST.get('sample_available') == 'on',
        )

        # M2M Relationships
        styles_ids = request.POST.getlist('styles')
        if styles_ids:
            product.styles.set(styles_ids)
        rooms_ids = request.POST.getlist('rooms')
        if rooms_ids:
            product.rooms.set(rooms_ids)
        shapes_ids = request.POST.getlist('shapes')
        if shapes_ids:
            product.shapes.set(shapes_ids)
        features_ids = request.POST.getlist('features')
        if features_ids:
            product.features.set(features_ids)

        # Multi-file Gallery Images upload
        gallery_files = request.FILES.getlist('gallery_images')
        for idx, g_file in enumerate(gallery_files):
            if g_file:
                g_url = save_uploaded_media(g_file, 'products', title=f"{product.name} Gallery Angle {idx+1}")
                ProductImage.objects.create(
                    product=product,
                    image_url=g_url,
                    caption=f"{product.name} Multi-Angle {idx+1}",
                    sort_order=idx + 1
                )

        # Parse submitted multiple sizes with their respective prices
        custom_sizes = request.POST.getlist('variant_size[]')
        custom_prices = request.POST.getlist('variant_price[]')
        custom_skus = request.POST.getlist('variant_sku[]')

        created_count = 0
        if custom_sizes:
            for idx, sz in enumerate(custom_sizes):
                sz = sz.strip()
                if not sz:
                    continue
                pr_str = custom_prices[idx] if idx < len(custom_prices) and custom_prices[idx] else str(price_from)
                try:
                    pr = Decimal(pr_str)
                except Exception:
                    pr = price_from
                sku = custom_skus[idx].strip() if idx < len(custom_skus) and custom_skus[idx] else ''
                if not sku:
                    clean_sz = sz.replace(' ', '').replace('"', '').replace("'", "")
                    sku = f"{catalog_code}-{clean_sz}"

                ProductVariant.objects.create(
                    product=product,
                    size=sz,
                    color_name="Signature Edition",
                    color_hex="#9D9B8B",
                    sku=sku,
                    price=pr,
                    in_stock=True,
                    variant_image=image_url
                )
                created_count += 1

        # If no custom sizes rows provided, seed 5 standard rug sizes automatically
        if created_count == 0:
            default_sizes = [
                ("18\" Swatch", Decimal('25.00')),
                ("6'X9'", price_from),
                ("8'X10'", (price_from * Decimal('1.45')).quantize(Decimal('1.00'))),
                ("9'X12'", (price_from * Decimal('1.95')).quantize(Decimal('1.00'))),
                ("10'X14'", (price_from * Decimal('2.65')).quantize(Decimal('1.00'))),
            ]
            for sz, pr in default_sizes:
                clean_sz = sz.replace(' ', '').replace('"', '').replace("'", "")
                ProductVariant.objects.create(
                    product=product,
                    size=sz,
                    color_name="Signature Edition",
                    color_hex="#9D9B8B",
                    sku=f"{catalog_code}-{clean_sz}",
                    price=pr,
                    in_stock=True,
                    variant_image=image_url
                )
                created_count += 1

        messages.success(request, f"Product '{name}' created with {created_count} size variants and advanced attributes!")
        return redirect('storefront:dashboard_products')

    ctx = {'active_tab': 'products', 'is_edit': False}
    ctx.update(get_taxonomy_context())
    return render(request, 'storefront/dashboard/product_form.html', ctx)

@require_http_methods(["GET", "POST"])
def dashboard_product_edit(request, product_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    product = get_object_or_404(Product.objects.prefetch_related('variants', 'styles', 'rooms', 'shapes'), id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.catalog_code = request.POST.get('catalog_code', '').strip().upper()
        product.collection = request.POST.get('collection', '').strip()
        category_id = request.POST.get('category')
        if category_id:
            product.category = get_object_or_404(Category, id=category_id)
        product.construction = request.POST.get('construction', product.construction)
        product.material = request.POST.get('material', product.material)
        product.origin = request.POST.get('origin', product.origin)
        product.pile_height = request.POST.get('pile_height', product.pile_height)
        product.price_from = Decimal(request.POST.get('price_from', str(product.price_from)))
        product.badge = request.POST.get('badge', '').strip()
        product.description = request.POST.get('description', '').strip() or DEFAULT_ARTISAN_STORY
        product.care_instructions = request.POST.get('care_instructions', '').strip() or DEFAULT_CARE_INSTRUCTIONS

        # Handle uploaded images with fallback to text URL
        if request.FILES.get('image_file'):
            product.image_url = save_uploaded_media(request.FILES.get('image_file'), 'products', title=f"{product.name} Primary Shot")
        elif request.POST.get('image_url'):
            product.image_url = request.POST.get('image_url').strip()

        if request.FILES.get('secondary_image_file'):
            product.secondary_image_url = save_uploaded_media(request.FILES.get('secondary_image_file'), 'products', title=f"{product.name} Texture")
        elif request.POST.get('secondary_image_url'):
            product.secondary_image_url = request.POST.get('secondary_image_url').strip()

        if request.FILES.get('lifestyle_image_file'):
            product.lifestyle_image_url = save_uploaded_media(request.FILES.get('lifestyle_image_file'), 'products', title=f"{product.name} Lifestyle")
        elif request.POST.get('lifestyle_image_url'):
            product.lifestyle_image_url = request.POST.get('lifestyle_image_url').strip()

        if request.FILES.get('video_file'):
            product.video_url = save_uploaded_media(request.FILES.get('video_file'), 'videos', title=f"{product.name} Video")
        elif 'video_url' in request.POST:
            product.video_url = request.POST.get('video_url', '').strip()

        if request.FILES.get('ar_model_file'):
            product.ar_model_url = save_uploaded_media(request.FILES.get('ar_model_file'), 'models3d', title=f"{product.name} 3D AR Model")
        elif 'ar_model_url' in request.POST:
            product.ar_model_url = request.POST.get('ar_model_url', '').strip()

        product.is_trending = request.POST.get('is_trending') == 'on'
        product.is_callaluxe = request.POST.get('is_callaluxe') == 'on'
        product.is_in_stock = request.POST.get('is_in_stock') == 'on'

        # Advanced Normalized Attributes
        product.collection_obj_id = request.POST.get('collection_obj') or None
        product.designer_id = request.POST.get('designer') or None
        product.primary_material_id = request.POST.get('primary_material') or None
        product.construction_type_id = request.POST.get('construction_type') or None
        product.primary_color_id = request.POST.get('primary_color') or None
        product.knot_count = request.POST.get('knot_count', product.knot_count).strip()
        product.traffic_rating = request.POST.get('traffic_rating', product.traffic_rating)
        product.backing = request.POST.get('backing', product.backing).strip()
        product.is_outdoor_safe = request.POST.get('is_outdoor_safe') == 'on'
        product.is_floor_heating_safe = request.POST.get('is_floor_heating_safe') == 'on'
        product.is_custom_size_available = request.POST.get('is_custom_size_available') == 'on'
        product.sample_available = request.POST.get('sample_available') == 'on'
        product.save()

        # Update M2M
        product.styles.set(request.POST.getlist('styles'))
        product.rooms.set(request.POST.getlist('rooms'))
        product.shapes.set(request.POST.getlist('shapes'))
        product.features.set(request.POST.getlist('features'))

        # Process multiple gallery images if uploaded
        gallery_files = request.FILES.getlist('gallery_images')
        for idx, g_file in enumerate(gallery_files):
            if g_file:
                g_url = save_uploaded_media(g_file, 'products', title=f"{product.name} Gallery View")
                ProductImage.objects.create(
                    product=product,
                    image_url=g_url,
                    caption=f"{product.name} Multi-Angle View",
                    sort_order=ProductImage.objects.filter(product=product).count() + 1
                )

        # Synchronize multiple sizes & prices submitted
        var_ids = request.POST.getlist('variant_id[]')
        sizes = request.POST.getlist('variant_size[]')
        prices = request.POST.getlist('variant_price[]')
        skus = request.POST.getlist('variant_sku[]')
        deleted_ids = request.POST.getlist('deleted_variant_ids[]')

        # Delete any removed variants
        for d_id in deleted_ids:
            if d_id.strip():
                try:
                    ProductVariant.objects.filter(id=int(d_id), product=product).delete()
                except Exception:
                    pass

        # Update or create each size variant
        for idx, sz in enumerate(sizes):
            sz = sz.strip()
            if not sz:
                continue
            pr_str = prices[idx] if idx < len(prices) and prices[idx] else str(product.price_from)
            try:
                pr_val = Decimal(pr_str)
            except Exception:
                pr_val = product.price_from

            sku_val = skus[idx].strip() if idx < len(skus) else ''
            if not sku_val:
                clean_sz = sz.replace(' ', '').replace('"', '').replace("'", "")
                sku_val = f"{product.catalog_code}-{clean_sz}"

            v_id_str = var_ids[idx] if idx < len(var_ids) else ''
            if v_id_str and v_id_str.isdigit():
                try:
                    v = ProductVariant.objects.get(id=int(v_id_str), product=product)
                    v.size = sz
                    v.price = pr_val
                    v.sku = sku_val
                    v.save()
                except ProductVariant.DoesNotExist:
                    pass
            else:
                ProductVariant.objects.create(
                    product=product,
                    size=sz,
                    color_name="Signature Palette",
                    color_hex="#9D9B8B",
                    sku=sku_val,
                    price=pr_val,
                    in_stock=True,
                    variant_image=product.image_url
                )

        messages.success(request, f"Product '{product.name}' and all attributes/sizes updated in database!")
        return redirect('storefront:dashboard_products')

    ctx = {'active_tab': 'products', 'product': product, 'is_edit': True}
    ctx.update(get_taxonomy_context())
    return render(request, 'storefront/dashboard/product_form.html', ctx)


@require_POST
def dashboard_product_delete(request, product_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f"Product '{name}' and all its variants have been deleted from the database.")
    return redirect('storefront:dashboard_products')

def dashboard_product_variants(request, product_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    product = get_object_or_404(Product.objects.prefetch_related('variants'), id=product_id)
    variants = product.variants.all().order_by('price')

    return render(request, 'storefront/dashboard/variants.html', {
        'active_tab': 'products',
        'product': product,
        'variants': variants,
    })

@require_POST
def dashboard_variant_create(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size', '').strip()
    color_name = request.POST.get('color_name', 'Signature Palette').strip()
    color_hex = request.POST.get('color_hex', '#A0987C').strip()
    price = Decimal(request.POST.get('price', '1500.00'))
    sku = request.POST.get('sku', '').strip()
    in_stock = request.POST.get('in_stock') == 'on'
    variant_image = request.POST.get('variant_image', product.image_url).strip()
    if request.FILES.get('variant_image_file'):
        variant_image = save_uploaded_media(request.FILES.get('variant_image_file'), 'variants', title=f"{product.name} - {size} Swatch")

    if not sku:
        clean_sz = size.replace(' ', '').replace('"', '').replace("'", "")
        sku = f"{product.catalog_code}-{clean_sz}"

    ProductVariant.objects.create(
        product=product,
        size=size,
        color_name=color_name,
        color_hex=color_hex,
        price=price,
        sku=sku,
        in_stock=in_stock,
        variant_image=variant_image
    )
    messages.success(request, f"Added size '{size}' (${price}) to {product.name}!")
    return redirect('storefront:dashboard_product_variants', product_id=product.id)

@require_POST
def dashboard_variants_batch_create(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    sizes = request.POST.getlist('size[]')
    prices = request.POST.getlist('price[]')
    skus = request.POST.getlist('sku[]')

    added_count = 0
    for idx, sz in enumerate(sizes):
        sz = sz.strip()
        if not sz:
            continue
        pr_str = prices[idx] if idx < len(prices) and prices[idx] else str(product.price_from)
        try:
            pr = Decimal(pr_str)
        except Exception:
            pr = product.price_from

        sku = skus[idx].strip() if idx < len(skus) and skus[idx] else ''
        if not sku:
            clean_sz = sz.replace(' ', '').replace('"', '').replace("'", "")
            sku = f"{product.catalog_code}-{clean_sz}"

        ProductVariant.objects.create(
            product=product,
            size=sz,
            color_name="Signature Palette",
            color_hex="#9D9B8B",
            price=pr,
            sku=sku,
            in_stock=True,
            variant_image=product.image_url
        )
        added_count += 1

    messages.success(request, f"Successfully added {added_count} new size variants to '{product.name}'!")
    return redirect('storefront:dashboard_product_variants', product_id=product.id)

@require_POST
def dashboard_variant_delete(request, variant_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    variant = get_object_or_404(ProductVariant, id=variant_id)
    product_id = variant.product_id
    size = variant.size
    variant.delete()
    messages.success(request, f"Variant size '{size}' deleted successfully.")
    return redirect('storefront:dashboard_product_variants', product_id=product_id)

@require_http_methods(["GET", "POST"])
def dashboard_cms(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    settings_obj = SiteSetting.get_settings()
    pages_list = list(PageContent.objects.all().order_by('id'))
    
    selected_page_key = request.POST.get('page_key') or request.GET.get('page') or 'home'
    current_page = PageContent.objects.filter(page_key=selected_page_key).first()

    # Auto-seed essential pages if missing when viewed
    if not current_page and selected_page_key != 'global':
        title_map = {
            'contact': ('Contact Us & Global Showrooms', 'Connect With AZI HOME', 'FLAGSHIP SHOWROOMS & CONCIERGE'),
            'customer_service': ('Customer Service & Concierge', 'Customer Service & Project Support', 'LUXURY CONCIERGE & CARE'),
            'privacy': ('Privacy Policy', 'Privacy Policy & Data Rights', 'TRANSPARENCY & TRUST'),
            'terms': ('Terms & Conditions', 'Terms & Conditions of Sale', 'TRADE & RETAIL AGREEMENT'),
            'refund': ('Refund & Return Policy', 'Refund, Return & Exchange Policy', 'EASY TRADE RETURNS & GUARANTEE'),
        }
        if selected_page_key in title_map:
            p_name, p_title, p_eyebrow = title_map[selected_page_key]
            current_page = PageContent.objects.create(
                page_key=selected_page_key,
                page_name=p_name,
                title=p_title,
                eyebrow=p_eyebrow,
                subtitle=f"Complete official details, specifications, and guidelines regarding our {p_name.lower()}."
            )

    live_url_map = {
        'home': '/',
        'story': '/the-jaipur-living-story/',
        'trade': '/become-a-partner/',
        'contract': '/contract/',
        'callaluxe': '/callaluxe/',
        'rugs': '/rugs/',
        'decor': '/decor/',
        'contact': '/contact-us/',
        'customer_service': '/customer-service/',
        'privacy': '/privacy-policy/',
        'terms': '/terms-and-conditions/',
        'refund': '/refund-and-return-policy/',
        'global': '/',
    }

    if request.method == 'POST':
        # 1. Update Global Header/Announcement & Brand Settings if submitted
        if selected_page_key == 'global' or request.POST.get('save_global') == '1':
            settings_obj.announcement_text = request.POST.get('announcement_text', settings_obj.announcement_text).strip()
            settings_obj.announcement_link_text = request.POST.get('announcement_link_text', settings_obj.announcement_link_text).strip()
            settings_obj.announcement_link_url = request.POST.get('announcement_link_url', settings_obj.announcement_link_url).strip()
            settings_obj.announcement_active = request.POST.get('announcement_active') == 'on'

            settings_obj.contact_phone = request.POST.get('contact_phone', settings_obj.contact_phone).strip()
            settings_obj.contact_email = request.POST.get('contact_email', settings_obj.contact_email).strip()
            settings_obj.trade_email = request.POST.get('trade_email', settings_obj.trade_email).strip()
            settings_obj.showroom_address = request.POST.get('showroom_address', settings_obj.showroom_address).strip()
            settings_obj.save()
            messages.success(request, "Global brand settings & announcement banner updated live!")
            return redirect(f"{reverse('storefront:dashboard_cms')}?page=global")

        # 2. Update Specific Page Content
        if current_page:
            current_page.eyebrow = request.POST.get('eyebrow', current_page.eyebrow).strip()
            current_page.title = request.POST.get('title', current_page.title).strip()
            current_page.subtitle = request.POST.get('subtitle', current_page.subtitle).strip()
            # Handle Hero Video Upload or URL
            if request.FILES.get('hero_video_file'):
                current_page.hero_video_url = save_uploaded_media(request.FILES.get('hero_video_file'), 'videos', title=f"{current_page.title} Hero Video")
            elif request.POST.get('hero_video_url'):
                current_page.hero_video_url = request.POST.get('hero_video_url').strip()

            # Handle Hero Image Upload or URL
            if request.FILES.get('hero_image_file'):
                current_page.hero_image = save_uploaded_media(request.FILES.get('hero_image_file'), 'cms', title=f"{current_page.title} Hero Image")
            elif request.POST.get('hero_image'):
                current_page.hero_image = request.POST.get('hero_image').strip()

            # Handle Secondary / Feature Image Upload or URL
            if request.FILES.get('secondary_image_file'):
                current_page.secondary_image = save_uploaded_media(request.FILES.get('secondary_image_file'), 'cms', title=f"{current_page.title} Feature Image")
            elif request.POST.get('secondary_image'):
                current_page.secondary_image = request.POST.get('secondary_image').strip()

            current_page.cta_primary_text = request.POST.get('cta_primary_text', current_page.cta_primary_text).strip()
            current_page.cta_primary_url = request.POST.get('cta_primary_url', current_page.cta_primary_url).strip()
            current_page.cta_secondary_text = request.POST.get('cta_secondary_text', current_page.cta_secondary_text).strip()
            current_page.cta_secondary_url = request.POST.get('cta_secondary_url', current_page.cta_secondary_url).strip()

            current_page.section_heading = request.POST.get('section_heading', current_page.section_heading).strip()
            current_page.section_subheading = request.POST.get('section_subheading', current_page.section_subheading).strip()
            current_page.body = request.POST.get('body', current_page.body).strip()
            current_page.highlight_text = request.POST.get('highlight_text', current_page.highlight_text).strip()
            current_page.meta_title = request.POST.get('meta_title', current_page.meta_title).strip()
            current_page.meta_description = request.POST.get('meta_description', current_page.meta_description).strip()
            current_page.save()

            # Harmonize homepage values with SiteSetting
            if selected_page_key == 'home':
                settings_obj.hero_eyebrow = current_page.eyebrow
                settings_obj.hero_title = current_page.title
                settings_obj.hero_subtitle = current_page.subtitle
                settings_obj.hero_cta_primary_text = current_page.cta_primary_text
                settings_obj.hero_cta_primary_url = current_page.cta_primary_url
                settings_obj.hero_cta_secondary_text = current_page.cta_secondary_text
                settings_obj.hero_cta_secondary_url = current_page.cta_secondary_url
                settings_obj.hero_video_url = current_page.hero_video_url
                if current_page.hero_image:
                    settings_obj.heritage_image_url = current_page.hero_image
                if current_page.highlight_text:
                    settings_obj.heritage_description = current_page.highlight_text
                settings_obj.save()

            messages.success(request, f"Page '{current_page.page_name}' content updated! Live website reflects all changes instantly.")
            return redirect(f"{reverse('storefront:dashboard_cms')}?page={selected_page_key}")

    return render(request, 'storefront/dashboard/cms.html', {
        'active_tab': 'cms',
        'active_page': selected_page_key,
        'current_page': current_page,
        'pages': pages_list,
        'settings': settings_obj,
        'live_url': live_url_map.get(selected_page_key, '/'),
    })

def dashboard_trade_apps(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    apps = TradeApplication.objects.order_by('-id')
    return render(request, 'storefront/dashboard/trade_apps.html', {
        'active_tab': 'trade_apps',
        'applications': apps,
    })

@require_POST
def dashboard_trade_toggle_approve(request, app_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    app_obj = get_object_or_404(TradeApplication, id=app_id)
    app_obj.approved = not app_obj.approved
    app_obj.save()
    status_str = "Approved" if app_obj.approved else "Pending Review"
    messages.success(request, f"Trade application for '{app_obj.company}' marked as {status_str}.")
    return redirect('storefront:dashboard_trade_apps')

def dashboard_subscribers(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    subs = NewsletterSubscriber.objects.order_by('-subscribed_at')
    return render(request, 'storefront/dashboard/subscribers.html', {
        'active_tab': 'subscribers',
        'subscribers': subs,
    })

def dashboard_db_tools(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    return render(request, 'storefront/dashboard/db_tools.html', {
        'active_tab': 'db_tools',
        'products_count': Product.objects.count(),
        'variants_count': ProductVariant.objects.count(),
        'categories_count': Category.objects.count(),
    })

def dashboard_export_json(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    data = []
    for p in Product.objects.all():
        data.append({
            'name': p.name,
            'catalog_code': p.catalog_code,
            'collection': p.collection,
            'construction': p.construction,
            'material': p.material,
            'price_from': float(p.price_from),
            'variants': [
                {'size': v.size, 'color': v.color_name, 'price': float(v.price), 'sku': v.sku}
                for v in p.variants.all()
            ]
        })
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="jaipur_living_catalog.json"'
    return response

@require_POST
def dashboard_reseed(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    import seed_data
    seed_data.seed()
    import seed_tierzah
    seed_tierzah.run()

    messages.success(request, "Database has been freshly re-seeded with all authentic AZI HOME catalog collections!")
    return redirect('storefront:dashboard_db_tools')

def dashboard_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            request.session['demo_admin_logged_in'] = True
            messages.success(request, f"Welcome back, {user.username}! Admin access granted.")
            return redirect('storefront:dashboard_home')
        else:
            messages.error(request, "Invalid username or password. You can also use the One-Click Superuser Access below.")

    return render(request, 'storefront/dashboard/login.html')

def dashboard_quick_login(request):
    """Convenient one-click superuser login for administrative evaluation."""
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@azi-home.com', 'admin123')
    login(request, user)
    request.session['demo_admin_logged_in'] = True
    messages.success(request, "Logged in as Administrator with Full Permissions.")
    return redirect('storefront:dashboard_home')

def dashboard_logout(request):
    logout(request)
    request.session.flush()
    messages.info(request, "You have been logged out of the admin dashboard.")
    return redirect('storefront:dashboard_login')

def dashboard_swatches(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    swatches = SwatchSampleRequest.objects.select_related('product', 'variant').order_by('-created_at')
    return render(request, 'storefront/dashboard/swatches.html', {
        'active_tab': 'swatches',
        'swatches': swatches,
    })

@require_POST
def dashboard_swatch_status(request, swatch_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    swatch = get_object_or_404(SwatchSampleRequest, id=swatch_id)
    new_status = request.POST.get('status', 'Shipped')
    tracking = request.POST.get('tracking_number', '').strip()
    swatch.status = new_status
    if tracking:
        swatch.tracking_number = tracking
    swatch.save()
    messages.success(request, f"Swatch request for {swatch.product.name} updated to '{new_status}'!")
    return redirect('storefront:dashboard_swatches')

def dashboard_reviews(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    reviews = CustomerReview.objects.select_related('product').order_by('-created_at')
    return render(request, 'storefront/dashboard/reviews.html', {
        'active_tab': 'reviews',
        'reviews': reviews,
    })

@require_POST
def dashboard_review_toggle(request, review_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    review = get_object_or_404(CustomerReview, id=review_id)
    review.is_approved = not review.is_approved
    review.save()
    status_str = "Approved & Live" if review.is_approved else "Hidden"
    messages.success(request, f"Review by {review.author_name} is now {status_str}.")
    return redirect('storefront:dashboard_reviews')

def dashboard_taxonomy(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    tab = request.GET.get('tab', 'overview')

    return render(request, 'storefront/dashboard/taxonomy.html', {
        'active_tab': 'taxonomy',
        'subtab': tab,
        'colors': Color.objects.all(),
        'sizes': Size.objects.all(),
        'materials': Material.objects.all(),
        'constructions': ConstructionType.objects.all(),
        'features': ProductFeature.objects.all(),
        'menu_items': MegaMenuItem.objects.all().order_by('section', 'sort_order', 'id'),
        'column_configs': MegaMenuColumnConfig.objects.all().order_by('sort_order', 'id'),
        'collections': RugCollection.objects.all(),
        'categories': Category.objects.all(),
        'designers': Designer.objects.all(),
        'styles': Style.objects.all(),
        'shapes': Shape.objects.all(),
        'rooms': RoomType.objects.all(),
        'color_families': Color.FAMILY_CHOICES,
        'size_types': Size.SIZE_TYPE_CHOICES,
        'menu_sections': MegaMenuItem.SECTION_CHOICES,
    })


@require_POST
def dashboard_taxonomy_create(request, entity_type):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    entity_type = entity_type.lower()
    try:
        if entity_type == 'color':
            name = request.POST.get('name', '').strip()
            hex_code = request.POST.get('hex_code', '#A0987C').strip()
            color_family = request.POST.get('color_family', 'Neutral').strip()
            if not name:
                messages.error(request, "Color name is required.")
            else:
                Color.objects.create(name=name, hex_code=hex_code, color_family=color_family)
                messages.success(request, f"Color '{name}' added successfully to the catalog palette!")

        elif entity_type == 'material':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            is_natural = request.POST.get('is_natural') == 'on'
            softness = int(request.POST.get('softness_score', 8) or 8)
            durability = int(request.POST.get('durability_score', 8) or 8)
            if not name:
                messages.error(request, "Material name is required.")
            else:
                Material.objects.create(
                    name=name,
                    description=description,
                    is_natural=is_natural,
                    softness_score=softness,
                    durability_score=durability,
                    eco_certified=is_natural
                )
                messages.success(request, f"Material '{name}' added successfully!")

        elif entity_type == 'construction':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            knot_count = request.POST.get('knot_count_typical', '80-120 KPSI').strip()
            lead_weeks = int(request.POST.get('production_lead_weeks', 12) or 12)
            heritage = request.POST.get('heritage_region', 'Bhadohi, India').strip()
            if not name:
                messages.error(request, "Construction technique name is required.")
            else:
                ConstructionType.objects.create(
                    name=name,
                    description=description,
                    knot_count_typical=knot_count,
                    production_lead_weeks=lead_weeks,
                    heritage_region=heritage
                )
                messages.success(request, f"Construction technique '{name}' added successfully!")

        elif entity_type == 'feature':
            name = request.POST.get('name', '').strip()
            icon = request.POST.get('icon', 'ri-shield-star-line').strip()
            description = request.POST.get('description', '').strip()
            is_highlighted = request.POST.get('is_highlighted') == 'on'
            sort_order = int(request.POST.get('sort_order', 0) or 0)
            if not name:
                messages.error(request, "Feature name is required.")
            else:
                ProductFeature.objects.create(
                    name=name,
                    icon=icon,
                    description=description,
                    is_highlighted=is_highlighted,
                    sort_order=sort_order
                )
                messages.success(request, f"Product feature '{name}' added successfully!")

        elif entity_type == 'size':
            label = request.POST.get('label', '').strip()
            size_type = request.POST.get('size_type', 'Area Rug')
            width = int(request.POST.get('width_inches', 0) or 0) or None
            length = int(request.POST.get('length_inches', 0) or 0) or None
            sqft = Decimal(request.POST.get('sqft', '0.00')) if request.POST.get('sqft') else None
            if not label:
                messages.error(request, "Size dimension label is required.")
            else:
                Size.objects.create(
                    label=label,
                    size_type=size_type,
                    width_inches=width,
                    length_inches=length,
                    sqft=sqft
                )
                messages.success(request, f"Size '{label}' added successfully!")

        elif entity_type in ['menu_item', 'menuitem']:
            section = request.POST.get('section', 'featured')
            title = request.POST.get('title', '').strip()
            url = request.POST.get('url', '/rugs/').strip()
            badge = request.POST.get('badge', '').strip()
            sort_order = int(request.POST.get('sort_order', 0) or 0)
            if not title:
                messages.error(request, "Menu item title is required.")
            else:
                MegaMenuItem.objects.create(
                    section=section,
                    title=title,
                    url=url,
                    badge=badge,
                    sort_order=sort_order,
                    is_active=True
                )
                messages.success(request, f"Mega-menu link '{title}' added to {section.capitalize()} section!")

        elif entity_type == 'collection':
            name = request.POST.get('name', '').strip()
            designer_id = request.POST.get('designer') or None
            tagline = request.POST.get('tagline', '').strip()
            description = request.POST.get('description', '').strip()
            launch_season = request.POST.get('launch_season', 'Fall / Winter 2026').strip()
            is_featured = request.POST.get('is_featured') == 'on'
            
            if request.FILES.get('hero_image_file'):
                hero_image = save_uploaded_media(request.FILES.get('hero_image_file'), 'collections', title=f"{name} Hero Banner")
            else:
                hero_image = request.POST.get('hero_image', '').strip()

            if not name:
                messages.error(request, "Collection name is required.")
            else:
                RugCollection.objects.create(
                    name=name,
                    designer_id=designer_id,
                    tagline=tagline,
                    description=description,
                    hero_image=hero_image,
                    launch_season=launch_season,
                    is_featured=is_featured
                )
                messages.success(request, f"Rug Collection '{name}' created successfully!")

        elif entity_type == 'category':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            image_url = request.POST.get('image_url', '').strip()
            if not name:
                messages.error(request, "Category name is required.")
            else:
                Category.objects.create(name=name, description=description, image_url=image_url)
                messages.success(request, f"Category '{name}' created successfully!")

    except Exception as e:
        messages.error(request, f"Error creating {entity_type}: {str(e)}")

    return redirect(f"{reverse('storefront:dashboard_taxonomy')}?tab={entity_type}")


@require_POST
def dashboard_taxonomy_edit(request, entity_type, item_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    entity_type = entity_type.lower()
    try:
        if entity_type == 'color':
            c = get_object_or_404(Color, id=item_id)
            c.name = request.POST.get('name', c.name).strip()
            c.hex_code = request.POST.get('hex_code', c.hex_code).strip()
            c.color_family = request.POST.get('color_family', c.color_family).strip()
            c.save()
            messages.success(request, f"Color '{c.name}' updated successfully!")

        elif entity_type == 'material':
            m = get_object_or_404(Material, id=item_id)
            m.name = request.POST.get('name', m.name).strip()
            m.description = request.POST.get('description', m.description).strip()
            m.is_natural = request.POST.get('is_natural') == 'on'
            m.softness_score = int(request.POST.get('softness_score', m.softness_score) or m.softness_score)
            m.durability_score = int(request.POST.get('durability_score', m.durability_score) or m.durability_score)
            m.save()
            messages.success(request, f"Material '{m.name}' updated successfully!")

        elif entity_type == 'construction':
            ct = get_object_or_404(ConstructionType, id=item_id)
            ct.name = request.POST.get('name', ct.name).strip()
            ct.description = request.POST.get('description', ct.description).strip()
            ct.knot_count_typical = request.POST.get('knot_count_typical', ct.knot_count_typical).strip()
            ct.production_lead_weeks = int(request.POST.get('production_lead_weeks', ct.production_lead_weeks) or ct.production_lead_weeks)
            ct.heritage_region = request.POST.get('heritage_region', ct.heritage_region).strip()
            ct.save()
            messages.success(request, f"Construction technique '{ct.name}' updated successfully!")

        elif entity_type == 'feature':
            f = get_object_or_404(ProductFeature, id=item_id)
            f.name = request.POST.get('name', f.name).strip()
            f.icon = request.POST.get('icon', f.icon).strip()
            f.description = request.POST.get('description', f.description).strip()
            f.is_highlighted = request.POST.get('is_highlighted') == 'on'
            f.sort_order = int(request.POST.get('sort_order', f.sort_order) or f.sort_order)
            f.save()
            messages.success(request, f"Product feature '{f.name}' updated successfully!")

        elif entity_type == 'size':
            s = get_object_or_404(Size, id=item_id)
            s.label = request.POST.get('label', s.label).strip()
            s.size_type = request.POST.get('size_type', s.size_type)
            s.width_inches = int(request.POST.get('width_inches', 0) or 0) or None
            s.length_inches = int(request.POST.get('length_inches', 0) or 0) or None
            s.sqft = Decimal(request.POST.get('sqft', '0.00')) if request.POST.get('sqft') else None
            s.save()
            messages.success(request, f"Size dimension '{s.label}' updated successfully!")

        elif entity_type in ['menu_item', 'menuitem']:
            item = get_object_or_404(MegaMenuItem, id=item_id)
            item.section = request.POST.get('section', item.section)
            item.title = request.POST.get('title', item.title).strip()
            item.url = request.POST.get('url', item.url).strip()
            item.badge = request.POST.get('badge', item.badge).strip()
            item.sort_order = int(request.POST.get('sort_order', item.sort_order) or item.sort_order)
            item.is_active = request.POST.get('is_active') == 'on'
            item.save()
            messages.success(request, f"Mega-menu link '{item.title}' updated successfully!")

        elif entity_type in ['mega_column', 'column']:
            col = get_object_or_404(MegaMenuColumnConfig, id=item_id)
            col.display_title = request.POST.get('display_title', col.display_title).strip()
            col.subtitle = request.POST.get('subtitle', col.subtitle).strip()
            col.is_visible = request.POST.get('is_visible') == 'on'
            col.sort_order = int(request.POST.get('sort_order', col.sort_order) or col.sort_order)
            col.promo_banner_active = request.POST.get('promo_banner_active') == 'on'
            col.promo_banner_title = request.POST.get('promo_banner_title', '').strip()
            col.promo_banner_link = request.POST.get('promo_banner_link', '').strip()
            if request.FILES.get('promo_banner_file'):
                col.promo_banner_image = save_uploaded_media(request.FILES.get('promo_banner_file'), 'megamenu', title=f"{col.display_title} Promo")
            elif request.POST.get('promo_banner_image'):
                col.promo_banner_image = request.POST.get('promo_banner_image').strip()
            col.save()
            messages.success(request, f"Mega-menu column '{col.display_title}' updated successfully!")

        elif entity_type == 'collection':
            col = get_object_or_404(RugCollection, id=item_id)
            col.name = request.POST.get('name', col.name).strip()
            col.designer_id = request.POST.get('designer') or None
            col.tagline = request.POST.get('tagline', col.tagline).strip()
            col.description = request.POST.get('description', col.description).strip()
            col.launch_season = request.POST.get('launch_season', col.launch_season).strip()
            col.is_featured = request.POST.get('is_featured') == 'on'
            if request.FILES.get('hero_image_file'):
                col.hero_image = save_uploaded_media(request.FILES.get('hero_image_file'), 'collections', title=f"{col.name} Hero Banner")
            elif request.POST.get('hero_image'):
                col.hero_image = request.POST.get('hero_image').strip()
            col.save()
            messages.success(request, f"Rug Collection '{col.name}' updated successfully!")

        elif entity_type == 'category':
            cat = get_object_or_404(Category, id=item_id)
            cat.name = request.POST.get('name', cat.name).strip()
            cat.description = request.POST.get('description', cat.description).strip()
            if request.POST.get('image_url'):
                cat.image_url = request.POST.get('image_url').strip()
            cat.save()
            messages.success(request, f"Category '{cat.name}' updated successfully!")

    except Exception as e:
        messages.error(request, f"Error updating {entity_type}: {str(e)}")

    return redirect(f"{reverse('storefront:dashboard_taxonomy')}?tab={entity_type}")


@require_POST
def dashboard_taxonomy_delete(request, entity_type, item_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    entity_type = entity_type.lower()
    try:
        model_map = {
            'color': Color,
            'material': Material,
            'construction': ConstructionType,
            'feature': ProductFeature,
            'size': Size,
            'menu_item': MegaMenuItem,
            'menuitem': MegaMenuItem,
            'collection': RugCollection,
            'category': Category,
            'mega_column': MegaMenuColumnConfig,
        }
        model_cls = model_map.get(entity_type)
        if not model_cls:
            messages.error(request, "Invalid entity type.")
            return redirect('storefront:dashboard_taxonomy')

        item = get_object_or_404(model_cls, id=item_id)
        item_name = getattr(item, 'name', getattr(item, 'label', getattr(item, 'title', getattr(item, 'display_title', str(item)))))
        item.delete()
        messages.success(request, f"{entity_type.capitalize()} '{item_name}' removed from database.")
    except Exception as e:
        messages.error(request, f"Error deleting {entity_type}: {str(e)}")

    return redirect(f"{reverse('storefront:dashboard_taxonomy')}?tab={entity_type}")


@require_http_methods(["GET", "POST"])
def dashboard_settings(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    site_settings = SiteSetting.get_settings()

    if request.method == 'POST':
        site_settings.site_name = request.POST.get('site_name', site_settings.site_name).strip()
        site_settings.announcement_text = request.POST.get('announcement_text', site_settings.announcement_text).strip()
        site_settings.announcement_link_text = request.POST.get('announcement_link_text', site_settings.announcement_link_text).strip()
        site_settings.announcement_link_url = request.POST.get('announcement_link_url', site_settings.announcement_link_url).strip()
        site_settings.announcement_bg_color = request.POST.get('announcement_bg_color', site_settings.announcement_bg_color).strip()
        site_settings.announcement_active = request.POST.get('announcement_active') == 'on'

        # Logo file upload or URL
        if request.FILES.get('header_logo_file'):
            site_settings.header_logo_url = save_uploaded_media(request.FILES.get('header_logo_file'), 'branding', title="Site Logo")
        elif request.POST.get('header_logo_url'):
            site_settings.header_logo_url = request.POST.get('header_logo_url').strip()

        try:
            site_settings.free_shipping_threshold = Decimal(request.POST.get('free_shipping_threshold', '500.00'))
        except Exception:
            pass

        site_settings.contact_phone = request.POST.get('contact_phone', site_settings.contact_phone).strip()
        site_settings.contact_email = request.POST.get('contact_email', site_settings.contact_email).strip()
        site_settings.trade_email = request.POST.get('trade_email', site_settings.trade_email).strip()
        site_settings.showroom_address = request.POST.get('showroom_address', site_settings.showroom_address).strip()

        site_settings.instagram_url = request.POST.get('instagram_url', '').strip()
        site_settings.pinterest_url = request.POST.get('pinterest_url', '').strip()
        site_settings.linkedin_url = request.POST.get('linkedin_url', '').strip()
        site_settings.youtube_url = request.POST.get('youtube_url', '').strip()
        site_settings.footer_copyright_text = request.POST.get('footer_copyright_text', site_settings.footer_copyright_text).strip()

        site_settings.save()
        messages.success(request, "Sitewide header, footer, announcement, and contact settings updated successfully!")
        return redirect('storefront:dashboard_settings')

    return render(request, 'storefront/dashboard/settings.html', {
        'active_tab': 'settings',
        'site_settings': site_settings,
    })


@require_POST
def dashboard_product_toggle_stock(request, product_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    product = get_object_or_404(Product, id=product_id)
    product.is_in_stock = not product.is_in_stock
    product.save()
    status_str = "In Stock" if product.is_in_stock else "Out of Stock"
    messages.success(request, f"'{product.name}' is now marked as {status_str}.")
    return redirect('storefront:dashboard_products')


@require_POST
def dashboard_product_toggle_trending(request, product_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    product = get_object_or_404(Product, id=product_id)
    product.is_trending = not product.is_trending
    product.save()
    status_str = "Trending" if product.is_trending else "Standard"
    messages.success(request, f"'{product.name}' is now marked as {status_str}.")
    return redirect('storefront:dashboard_products')


@require_POST
def dashboard_product_duplicate(request, product_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    source = get_object_or_404(Product, id=product_id)
    new_code = f"{source.catalog_code}-COPY" if source.catalog_code else f"COPY-{uuid.uuid4().hex[:4].upper()}"
    new_name = f"{source.name} (Copy)"
    new_slug = f"{source.slug}-copy-{uuid.uuid4().hex[:4]}"

    new_prod = Product.objects.create(
        name=new_name,
        catalog_code=new_code,
        slug=new_slug,
        collection=source.collection,
        category=source.category,
        collection_obj=source.collection_obj,
        designer=source.designer,
        primary_material=source.primary_material,
        construction_type=source.construction_type,
        primary_color=source.primary_color,
        construction=source.construction,
        material=source.material,
        origin=source.origin,
        pile_height=source.pile_height,
        pile_thickness_type=source.pile_thickness_type,
        knot_count=source.knot_count,
        backing=source.backing,
        traffic_rating=source.traffic_rating,
        is_outdoor_safe=source.is_outdoor_safe,
        is_floor_heating_safe=source.is_floor_heating_safe,
        is_custom_size_available=source.is_custom_size_available,
        sample_available=source.sample_available,
        artisan_days_to_craft=source.artisan_days_to_craft,
        description=source.description,
        care_instructions=source.care_instructions,
        image_url=source.image_url,
        secondary_image_url=source.secondary_image_url,
        lifestyle_image_url=source.lifestyle_image_url,
        video_url=source.video_url,
        ar_model_url=source.ar_model_url,
        price_from=source.price_from,
        badge="New Copy",
        is_callaluxe=source.is_callaluxe,
        is_trending=False,
        is_in_stock=True,
    )

    # Copy M2M
    new_prod.styles.set(source.styles.all())
    new_prod.rooms.set(source.rooms.all())
    new_prod.shapes.set(source.shapes.all())
    new_prod.features.set(source.features.all())

    # Copy Variants
    for v in source.variants.all():
        ProductVariant.objects.create(
            product=new_prod,
            size=v.size,
            color_name=v.color_name,
            color_hex=v.color_hex,
            sku=f"{v.sku}-COPY",
            price=v.price,
            in_stock=v.in_stock,
            variant_image=v.variant_image
        )



    messages.success(request, f"Product '{new_name}' duplicated with all sizes, images, and features!")
    return redirect('storefront:dashboard_product_edit', product_id=new_prod.id)


@require_POST
def dashboard_products_bulk_action(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    action = request.POST.get('bulk_action', '').strip()
    selected_ids = request.POST.getlist('selected_products')

    if not selected_ids:
        messages.warning(request, "No products selected for bulk action.")
        return redirect('storefront:dashboard_products')

    int_ids = [int(x) for x in selected_ids if x.isdigit()]
    qs = Product.objects.filter(id__in=int_ids)
    count = qs.count()

    if action == 'mark_in_stock':
        qs.update(is_in_stock=True)
        messages.success(request, f"{count} product(s) marked as In Stock.")
    elif action == 'mark_out_of_stock':
        qs.update(is_in_stock=False)
        messages.success(request, f"{count} product(s) marked as Out of Stock.")
    elif action == 'mark_trending':
        qs.update(is_trending=True)
        messages.success(request, f"{count} product(s) marked as Trending.")
    elif action == 'remove_trending':
        qs.update(is_trending=False)
        messages.success(request, f"{count} product(s) removed from Trending.")
    elif action == 'delete':
        qs.delete()
        messages.success(request, f"{count} product(s) deleted from catalog.")
    else:
        messages.error(request, "Unknown bulk action.")

    return redirect('storefront:dashboard_products')




def dashboard_media_library(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    media_type = request.GET.get('type', 'all')
    search_q = request.GET.get('q', '').strip()

    assets = MediaAsset.objects.all()

    if media_type and media_type != 'all':
        assets = assets.filter(file_type=media_type)

    if search_q:
        assets = assets.filter(Q(title__icontains=search_q) | Q(file_name__icontains=search_q))

    # Aggregates / Statistics
    total_count = MediaAsset.objects.count()
    images_count = MediaAsset.objects.filter(file_type='image').count()
    videos_count = MediaAsset.objects.filter(file_type='video').count()
    models3d_count = MediaAsset.objects.filter(file_type='model3d').count()
    documents_count = MediaAsset.objects.filter(file_type='document').count()
    other_count = MediaAsset.objects.filter(file_type='other').count()
    total_bytes = MediaAsset.objects.aggregate(total=Sum('file_size'))['total'] or 0

    if total_bytes < 1024:
        total_storage_formatted = f"{total_bytes} B"
    elif total_bytes < 1024 * 1024:
        total_storage_formatted = f"{total_bytes / 1024:.1f} KB"
    else:
        total_storage_formatted = f"{total_bytes / (1024 * 1024):.2f} MB"

    return render(request, 'storefront/dashboard/media_library.html', {
        'active_tab': 'media',
        'assets': assets,
        'current_type': media_type,
        'search_q': search_q,
        'total_count': total_count,
        'images_count': images_count,
        'videos_count': videos_count,
        'models3d_count': models3d_count,
        'documents_count': documents_count,
        'other_count': other_count,
        'total_storage_formatted': total_storage_formatted,
    })


@require_POST
def dashboard_media_upload(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    # Support multiple files via 'files' or single file via 'file'
    uploaded_files = request.FILES.getlist('files')
    if not uploaded_files and request.FILES.get('file'):
        uploaded_files = [request.FILES.get('file')]

    custom_title = request.POST.get('title', '').strip()
    uploaded_assets = []

    for f in uploaded_files:
        if f:
            title = custom_title if (custom_title and len(uploaded_files) == 1) else f.name
            url = save_uploaded_media(f, 'uploads', title=title)
            asset = MediaAsset.objects.filter(file_url=url).first()
            if asset:
                uploaded_assets.append({
                    'id': asset.id,
                    'title': asset.title,
                    'file_name': asset.file_name,
                    'file_url': asset.file_url,
                    'file_type': asset.file_type,
                    'formatted_size': asset.formatted_size,
                })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'count': len(uploaded_assets),
            'assets': uploaded_assets,
            'message': f"Successfully uploaded {len(uploaded_assets)} media asset(s)."
        })

    messages.success(request, f"Successfully uploaded {len(uploaded_files)} media asset(s) to the Media Library!")
    return redirect('storefront:dashboard_media_library')


@require_POST
def dashboard_media_delete(request, asset_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    asset = get_object_or_404(MediaAsset, id=asset_id)
    file_name = asset.file_name

    # Try deleting physical file from storage if within MEDIA_URL
    if asset.file_url and asset.file_url.startswith(settings.MEDIA_URL):
        rel_path = asset.file_url[len(settings.MEDIA_URL):]
        if default_storage.exists(rel_path):
            try:
                default_storage.delete(rel_path)
            except Exception:
                pass

    asset.delete()
    messages.success(request, f"Media asset '{file_name}' deleted successfully.")
    return redirect('storefront:dashboard_media_library')


def dashboard_inquiries(request):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    filter_type = request.GET.get('type', 'all')
    inquiries = ContactInquiry.objects.all().order_by('-created_at')
    if filter_type and filter_type != 'all':
        inquiries = inquiries.filter(inquiry_type=filter_type)

    total_count = ContactInquiry.objects.count()
    pending_count = ContactInquiry.objects.filter(is_resolved=False).count()

    return render(request, 'storefront/dashboard/inquiries.html', {
        'active_tab': 'inquiries',
        'inquiries': inquiries,
        'current_type': filter_type,
        'total_count': total_count,
        'pending_count': pending_count,
    })


@require_POST
def dashboard_inquiry_toggle(request, inquiry_id):
    if not check_admin_auth(request):
        return redirect('storefront:dashboard_login')

    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    inquiry.is_resolved = not inquiry.is_resolved
    inquiry.save()
    status_str = "Resolved" if inquiry.is_resolved else "Pending"
    messages.success(request, f"Inquiry from {inquiry.full_name} marked as {status_str}.")
    return redirect('storefront:dashboard_inquiries')
