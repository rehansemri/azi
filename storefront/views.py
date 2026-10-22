import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db.models import Count, Q
from .models import Category, Product, ProductVariant, TradeApplication, NewsletterSubscriber, PageContent, ContactInquiry, SiteSetting

def get_cart_data(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = Decimal('0.00')
    total_qty = 0

    for item_key, item in cart.items():
        subtotal = Decimal(str(item.get('price', '0'))) * int(item.get('quantity', 1))
        total_price += subtotal
        total_qty += int(item.get('quantity', 1))
        cart_items.append({
            'key': item_key,
            'product_id': item.get('product_id'),
            'name': item.get('name'),
            'size': item.get('size'),
            'color': item.get('color'),
            'price': float(item.get('price', 0)),
            'quantity': item.get('quantity', 1),
            'image': item.get('image'),
            'subtotal': float(subtotal),
        })

    return {
        'items': cart_items,
        'total_qty': total_qty,
        'total_price': float(total_price),
        'free_shipping_threshold': 500.0,
        'has_free_shipping': float(total_price) >= 500.0,
        'amount_needed_for_free_shipping': max(0.0, 500.0 - float(total_price)),
    }

@ensure_csrf_cookie
def index(request):
    callaluxe_products = Product.objects.filter(is_callaluxe=True).prefetch_related('variants')[:8]
    trending_products = Product.objects.filter(is_trending=True).order_by('-id').prefetch_related('variants')[:8]
    majnun_products = Product.objects.filter(collection__iexact='Majnun').prefetch_related('variants')[:6]
    page_content = PageContent.objects.filter(page_key='home').first()

    context = {
        'page_content': page_content,
        'callaluxe_products': callaluxe_products,
        'trending_products': trending_products,
        'majnun_products': majnun_products,
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    }
    return render(request, 'storefront/index.html', context)

def rugs_catalog(request, is_new=False, collection_filter=None):
    # Base queryset for rugs
    base_qs = Product.objects.filter(category__slug='rugs').prefetch_related('variants')

    page_title = "All Handcrafted Rugs"
    page_subtitle = "Woven knot by knot in Rajasthan, India"

    if is_new or request.GET.get('is_new') in ['1', 'true', 'True'] or request.GET.get('collection') == 'new':
        is_new = True
        page_title = "New Arrivals — Handcrafted Rugs"
        page_subtitle = "Freshly unrolled designer creations and seasonal palettes"

    if collection_filter:
        page_title = f"{collection_filter} Collection"
        page_subtitle = f"Signature designs from the {collection_filter} collection"

    # Dynamic filter facets fetched directly from the database
    all_collections_db = list(
        Product.objects.filter(category__slug='rugs')
        .values('collection')
        .annotate(total=Count('id'))
        .order_by('collection')
    )
    all_constructions_db = list(
        Product.objects.filter(category__slug='rugs')
        .values('construction')
        .annotate(total=Count('id'))
        .order_by('construction')
    )
    all_materials_db = list(
        Product.objects.filter(category__slug='rugs')
        .values('material')
        .annotate(total=Count('id'))
        .order_by('material')
    )
    all_sizes_db = list(
        ProductVariant.objects.filter(product__category__slug='rugs')
        .values('size')
        .annotate(total=Count('product_id', distinct=True))
        .order_by('-total')
    )

    price_tiers = [
        {'id': 'under-1500', 'label': 'Under $1,500', 'min': 0, 'max': 1500},
        {'id': '1500-3000', 'label': '$1,500 – $3,000', 'min': 1500, 'max': 3000},
        {'id': '3000-6000', 'label': '$3,000 – $6,000', 'min': 3000, 'max': 6000},
        {'id': 'over-6000', 'label': 'Over $6,000', 'min': 6000, 'max': 999999},
    ]
    for tier in price_tiers:
        tier['count'] = Product.objects.filter(category__slug='rugs', price_from__gte=tier['min'], price_from__lt=tier['max']).count()

    # Query filtering
    products = base_qs

    # Selected collections
    selected_collections = [c.strip() for c in request.GET.getlist('collection') if c.strip()]
    if collection_filter and collection_filter not in selected_collections:
        selected_collections.append(collection_filter)
    
    clean_collections = [c for c in selected_collections if c.lower() not in ['new', 'all', 'bestsellers']]
    if clean_collections:
        products = products.filter(collection__in=clean_collections)

    # Selected constructions
    selected_constructions = [c.strip() for c in request.GET.getlist('construction') if c.strip()]
    if selected_constructions:
        const_q = Q()
        for c in selected_constructions:
            const_q |= Q(construction_type__name__icontains=c) | Q(construction_type__slug__iexact=c) | Q(construction__icontains=c)
        products = products.filter(const_q).distinct()

    # Selected materials
    selected_materials = [m.strip() for m in request.GET.getlist('material') if m.strip()]
    if selected_materials:
        mat_q = Q()
        for m in selected_materials:
            mat_q |= Q(primary_material__name__icontains=m) | Q(primary_material__slug__iexact=m) | Q(material__icontains=m)
        products = products.filter(mat_q).distinct()

    # Selected colors
    selected_colors = [c.strip() for c in request.GET.getlist('color') if c.strip()]
    if selected_colors:
        color_q = Q()
        for c in selected_colors:
            color_q |= Q(primary_color__name__iexact=c) | Q(primary_color__slug__iexact=c) | Q(primary_color__color_family__iexact=c) | Q(name__icontains=c)
        products = products.filter(color_q).distinct()

    # Selected features
    selected_features = [f.strip() for f in request.GET.getlist('feature') if f.strip()]
    if selected_features:
        feat_q = Q()
        for f in selected_features:
            feat_q |= Q(features__name__icontains=f) | Q(features__slug__icontains=f)
        products = products.filter(feat_q).distinct()

    # Featured menu filters
    featured_filter = request.GET.get('featured', '').strip().lower()
    if featured_filter == 'new':
        products = products.order_by('-id')
    elif featured_filter == 'bestsellers':
        products = products.filter(is_trending=True)
    elif featured_filter == 'warehouse':
        products = products.filter(is_in_stock=True)
    elif featured_filter == 'designers':
        products = products.filter(Q(designer__isnull=False) | Q(collection__icontains='Vern Yip')).distinct()
    elif featured_filter == 'vintage':
        products = products.filter(Q(features__name__icontains='Vintage') | Q(name__icontains='Vintage') | Q(collection__icontains='Vintage')).distinct()

    # Selected sizes
    selected_sizes = [s.strip() for s in request.GET.getlist('size') if s.strip()]
    if selected_sizes:
        size_q = Q()
        for sz in selected_sizes:
            clean_sz = sz.replace("'", "").replace('"', '').replace(' ', '').upper()
            size_q |= Q(variants__size__icontains=sz) | Q(variants__size__icontains=clean_sz)
            if 'RUNNER' in clean_sz:
                size_q |= Q(variants__size__icontains='Runner')
        products = products.filter(size_q).distinct()

    # Selected price tiers
    selected_prices = [p.strip() for p in request.GET.getlist('price') if p.strip()]
    if selected_prices:
        price_q = Q()
        for p_id in selected_prices:
            match_t = next((t for t in price_tiers if t['id'] == p_id), None)
            if match_t:
                price_q |= Q(price_from__gte=match_t['min'], price_from__lt=match_t['max'])
        products = products.filter(price_q)

    # In stock filter
    in_stock_only = request.GET.get('in_stock') in ['1', 'true', 'True']
    if in_stock_only:
        products = products.filter(is_in_stock=True)

    # Search keyword
    search_q = request.GET.get('q', '').strip()
    if search_q:
        products = products.filter(
            Q(name__icontains=search_q) |
            Q(description__icontains=search_q) |
            Q(catalog_code__icontains=search_q) |
            Q(collection__icontains=search_q)
        ).distinct()

    # Sorting
    sort_by = request.GET.get('sort', 'newest' if is_new else 'featured')
    if sort_by == 'newest':
        products = products.order_by('-id')
    elif sort_by == 'price_asc':
        products = products.order_by('price_from')
    elif sort_by == 'price_desc':
        products = products.order_by('-price_from')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    else:
        products = products.order_by('-is_trending', '-id')

    # Construct active filter pills for easy removal
    active_filter_pills = []
    for c in clean_collections:
        active_filter_pills.append({'type': 'collection', 'val': c, 'label': f"Collection: {c}"})
    for c in selected_constructions:
        active_filter_pills.append({'type': 'construction', 'val': c, 'label': f"Construction: {c}"})
    for m in selected_materials:
        active_filter_pills.append({'type': 'material', 'val': m, 'label': f"Material: {m}"})
    for s in selected_sizes:
        active_filter_pills.append({'type': 'size', 'val': s, 'label': f"Size: {s}"})
    for p in selected_prices:
        t = next((t for t in price_tiers if t['id'] == p), None)
        if t:
            active_filter_pills.append({'type': 'price', 'val': p, 'label': f"Price: {t['label']}"})
    if in_stock_only:
        active_filter_pills.append({'type': 'in_stock', 'val': '1', 'label': "In Stock Only"})

    context = {
        'products': products,
        'page_title': page_title,
        'page_subtitle': page_subtitle,
        'is_new_page': is_new,
        'all_collections': all_collections_db,
        'all_constructions': all_constructions_db,
        'all_materials': all_materials_db,
        'all_sizes': all_sizes_db,
        'price_tiers': price_tiers,
        'selected_collections': clean_collections,
        'selected_constructions': selected_constructions,
        'selected_materials': selected_materials,
        'selected_sizes': selected_sizes,
        'selected_prices': selected_prices,
        'in_stock_only': in_stock_only,
        'current_sort': sort_by,
        'search_query': search_q,
        'active_filter_pills': active_filter_pills,
        'total_count': products.count(),
        'page_content': PageContent.objects.filter(page_key='rugs').first(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    }
    return render(request, 'storefront/rugs.html', context)

def rugs_new_catalog(request):
    return rugs_catalog(request, is_new=True)

def rugs_collection_catalog(request, collection_slug):
    clean = collection_slug.removesuffix('.html').replace('-', ' ')
    matching_prod = Product.objects.filter(collection__iexact=clean).first()
    coll_name = matching_prod.collection if matching_prod else clean.title()
    return rugs_catalog(request, collection_filter=coll_name)

def decor_catalog(request):
    products = Product.objects.filter(category__slug='decor').prefetch_related('variants')
    
    # Dynamic collections from DB
    all_collections_db = list(
        Product.objects.filter(category__slug='decor')
        .values('collection')
        .annotate(total=Count('id'))
        .order_by('collection')
    )
    
    selected_collection = request.GET.get('collection', '').strip()
    if selected_collection:
        products = products.filter(collection__iexact=selected_collection)

    context = {
        'page_content': PageContent.objects.filter(page_key='decor').first(),
        'products': products,
        'all_collections': all_collections_db,
        'selected_collection': selected_collection,
        'total_count': products.count(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    }
    return render(request, 'storefront/decor.html', context)

def callaluxe_page(request):
    products = Product.objects.filter(is_callaluxe=True).prefetch_related('variants')
    context = {
        'page_content': PageContent.objects.filter(page_key='callaluxe').first(),
        'products': products,
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    }
    return render(request, 'storefront/callaluxe.html', context)

def product_detail(request, slug):
    clean_slug = slug.removesuffix('.html') if slug.endswith('.html') else slug
    product = get_object_or_404(Product.objects.prefetch_related('variants', 'gallery_images'), slug=clean_slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    variants = list(product.variants.all())
    gallery_images = list(product.gallery_images.all())
    
    unique_colors = []
    seen_colors = set()
    for v in variants:
        if v.color_name not in seen_colors:
            seen_colors.add(v.color_name)
            # Find matching sister product if exists
            sister_code = "TRZ04" if "TRZ04" in v.color_name else ("TRZ05" if "TRZ05" in v.color_name else "")
            sister_product = Product.objects.filter(catalog_code=sister_code).first() if sister_code else None
            unique_colors.append({
                'name': v.color_name,
                'hex': v.color_hex,
                'image': v.variant_image or product.image_url,
                'code': sister_code or product.catalog_code,
                'product_url': f"/{sister_product.slug}.html" if sister_product else None,
            })

    # Default colorway
    default_color = unique_colors[0]['name'] if unique_colors else ''

    # Build size options directly from database variants
    size_options = []
    seen_sizes = set()
    for v in variants:
        if v.size not in seen_sizes:
            seen_sizes.add(v.size)
            # Find matching variant for default color if possible, else current v
            match_var = next((var for var in variants if var.size == v.size and var.color_name == default_color), v)
            p_val = float(match_var.price)
            msrp_val = round(p_val * 2.16, 2) if p_val > 50 else round(p_val * 2.0, 2)
            savings_pct = int(round((1 - p_val / msrp_val) * 100)) if msrp_val > 0 else 0
            size_options.append({
                'size': v.size,
                'price': p_val,
                'msrp': msrp_val,
                'savings': f"Save {savings_pct}%",
                'sku': match_var.sku or f"{product.catalog_code}-{v.size.replace(' ', '')}",
                'in_stock': match_var.in_stock,
            })

    # Pick default active size (prefer 8'X10' if available, otherwise first size in DB)
    default_size_opt = next((s for s in size_options if "8'X10'" in s['size'] or "8'x10'" in s['size'].lower()), size_options[0] if size_options else None)

    # Full database variants serialized as JSON (NO hardcoding!)
    db_variants_json = json.dumps([
        {
            'id': v.id,
            'size': v.size,
            'color': v.color_name,
            'sku': v.sku or f"{product.catalog_code}-{v.size.replace(' ', '')}",
            'price': float(v.price),
            'msrp': round(float(v.price) * 2.16, 2) if float(v.price) > 50 else round(float(v.price) * 2.0, 2),
            'savings_pct': int(round((1 - float(v.price) / (float(v.price) * 2.16 if float(v.price) > 50 else float(v.price) * 2.0)) * 100)),
            'in_stock': v.in_stock,
            'image': v.variant_image or product.image_url,
        }
        for v in variants
    ])

    context = {
        'product': product,
        'variants': variants,
        'db_variants_json': db_variants_json,
        'size_options': size_options,
        'default_size_option': default_size_opt,
        'unique_colors': unique_colors,
        'gallery_images': gallery_images,
        'related_products': related_products,
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    }
    return render(request, 'storefront/product_detail.html', context)

def story_page(request):
    return render(request, 'storefront/story.html', {
        'page_content': PageContent.objects.filter(page_key='story').first(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })

def trade_page(request):
    return render(request, 'storefront/trade.html', {
        'page_content': PageContent.objects.filter(page_key='trade').first(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })

def contract_page(request):
    return render(request, 'storefront/contract.html', {
        'page_content': PageContent.objects.filter(page_key='contract').first(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })

# API endpoints
def api_product_quick_view(request, product_id):
    product = get_object_or_404(Product.objects.prefetch_related('variants'), id=product_id)
    variants = list(product.variants.all())
    
    data = {
        'id': product.id,
        'name': product.name,
        'code': product.catalog_code,
        'collection': product.collection,
        'construction': product.construction,
        'material': product.material,
        'origin': product.origin,
        'pile_height': product.pile_height,
        'description': product.description,
        'price_from': float(product.price_from),
        'image': product.image_url,
        'secondary_image': product.secondary_image_url or product.image_url,
        'lifestyle_image': product.lifestyle_image_url or product.image_url,
        'variants': [
            {
                'id': v.id,
                'size': v.size,
                'color_name': v.color_name,
                'color_hex': v.color_hex,
                'price': float(v.price),
                'image': v.variant_image or product.image_url,
            }
            for v in variants
        ],
    }
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def api_cart(request):
    cart = request.session.get('cart', {})

    if request.method == 'GET':
        return JsonResponse(get_cart_data(request))

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            body = request.POST

        product_id = body.get('product_id')
        size = body.get('size', '8\'X10\'')
        color = body.get('color', 'Default')
        quantity = int(body.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        
        # Check variant price
        variant = ProductVariant.objects.filter(product=product, size=size, color_name=color).first()
        if not variant:
            variant = ProductVariant.objects.filter(product=product, size=size).first()
        
        price = float(variant.price) if variant else float(product.price_from)
        img = variant.variant_image if (variant and variant.variant_image) else product.image_url

        key = f"{product_id}_{size}_{color}".replace(" ", "_")
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {
                'product_id': product.id,
                'name': product.name,
                'size': size,
                'color': color,
                'price': price,
                'quantity': quantity,
                'image': img,
            }

        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'success': True, 'message': f'Added {product.name} to cart', 'cart': get_cart_data(request)})

    elif request.method == 'DELETE':
        try:
            body = json.loads(request.body.decode('utf-8'))
            key = body.get('key')
        except Exception:
            key = request.GET.get('key')

        if key and key in cart:
            del cart[key]
            request.session['cart'] = cart
            request.session.modified = True

        return JsonResponse({'success': True, 'cart': get_cart_data(request)})

@csrf_exempt
@require_POST
def api_wishlist_toggle(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = request.POST

    product_id = int(body.get('product_id', 0))
    wishlist = request.session.get('wishlist', [])

    if product_id in wishlist:
        wishlist.remove(product_id)
        status = 'removed'
    else:
        wishlist.append(product_id)
        status = 'added'

    request.session['wishlist'] = wishlist
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'status': status,
        'count': len(wishlist),
        'product_id': product_id
    })

@csrf_exempt
@require_POST
def api_trade_apply(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    company = data.get('company', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    business_type = data.get('business_type', 'Interior Designer')
    website = data.get('website', '').strip()
    notes = data.get('notes', '').strip()

    if not first_name or not last_name or not company or not email:
        return JsonResponse({'success': False, 'message': 'Please fill in all required fields marked with *.'}, status=400)

    application = TradeApplication.objects.create(
        first_name=first_name,
        last_name=last_name,
        company=company,
        email=email,
        phone=phone,
        business_type=business_type,
        website=website,
        notes=notes,
    )

    return JsonResponse({
        'success': True,
        'message': f'Thank you, {first_name}! Your trade application for {company} has been received. Our trade specialist will review and contact you shortly.'
    })

@csrf_exempt
@require_POST
def api_newsletter(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    email = data.get('email', '').strip()
    if not email or '@' not in email:
        return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'}, status=400)

    NewsletterSubscriber.objects.get_or_create(email=email)
    return JsonResponse({
        'success': True,
        'message': 'Welcome to AZI HOME! You are now subscribed to our exclusive design previews and trade announcements.'
    })


# ==========================================
# ESSENTIAL PAGES: CONTACT, CUSTOMER SERVICE,
# PRIVACY, TERMS & REFUND (CMS-EDITABLE)
# ==========================================

def contact_page(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        inquiry_type = request.POST.get('inquiry_type', 'general')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if full_name and email and message:
            ContactInquiry.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                inquiry_type=inquiry_type,
                subject=subject or 'General Inquiry',
                message=message
            )
            return render(request, 'storefront/contact.html', {
                'page_content': PageContent.objects.filter(page_key='contact').first(),
                'settings': SiteSetting.get_settings(),
                'cart_data': get_cart_data(request),
                'wishlist_count': len(request.session.get('wishlist', [])),
                'submitted': True,
                'submitted_name': full_name,
            })

    return render(request, 'storefront/contact.html', {
        'page_content': PageContent.objects.filter(page_key='contact').first(),
        'settings': SiteSetting.get_settings(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })


def customer_service_page(request):
    return render(request, 'storefront/customer_service.html', {
        'page_content': PageContent.objects.filter(page_key='customer_service').first(),
        'settings': SiteSetting.get_settings(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })


def privacy_policy_page(request):
    return render(request, 'storefront/privacy.html', {
        'page_content': PageContent.objects.filter(page_key='privacy').first(),
        'settings': SiteSetting.get_settings(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })


def terms_conditions_page(request):
    return render(request, 'storefront/terms.html', {
        'page_content': PageContent.objects.filter(page_key='terms').first(),
        'settings': SiteSetting.get_settings(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })


def refund_policy_page(request):
    return render(request, 'storefront/refund.html', {
        'page_content': PageContent.objects.filter(page_key='refund').first(),
        'settings': SiteSetting.get_settings(),
        'cart_data': get_cart_data(request),
        'wishlist_count': len(request.session.get('wishlist', [])),
    })


@csrf_exempt
@require_POST
def api_contact_submit(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    inquiry_type = data.get('inquiry_type', 'general')
    subject = data.get('subject', '').strip() or 'Project / Rug Inquiry'
    message = data.get('message', '').strip()

    if not full_name or not email or not message:
        return JsonResponse({'success': False, 'message': 'Please provide your name, email, and message.'}, status=400)

    inquiry = ContactInquiry.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        inquiry_type=inquiry_type,
        subject=subject,
        message=message
    )

    return JsonResponse({
        'success': True,
        'message': f'Thank you, {full_name}. Your inquiry (#{inquiry.id}) has been delivered to our concierge team. We will respond within 24 hours.'
    })
