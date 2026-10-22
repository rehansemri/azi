from decimal import Decimal
from django.db import models
from django.utils.text import slugify

# ==========================================
# 1. TAXONOMY & ATTRIBUTE ENTITIES
# ==========================================

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, max_length=500)
    banner_image = models.URLField(blank=True, max_length=500)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Designer(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    title = models.CharField(max_length=150, blank=True, default="Featured Guest Designer")
    bio = models.TextField(blank=True)
    portrait_image = models.URLField(blank=True, max_length=500)
    banner_image = models.URLField(blank=True, max_length=500)
    website = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class RugCollection(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    designer = models.ForeignKey(Designer, on_delete=models.SET_NULL, null=True, blank=True, related_name='collections')
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    hero_image = models.URLField(blank=True, max_length=500)
    lifestyle_image = models.URLField(blank=True, max_length=500)
    launch_season = models.CharField(max_length=100, blank=True, default="Fall / Winter 2026")
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Color(models.Model):
    FAMILY_CHOICES = [
        ('Blue', 'Blues & Navies'),
        ('Neutral', 'Neutrals, Creams & Ivories'),
        ('Gray', 'Grays & Charcoals'),
        ('Earth', 'Earth, Terracotta & Rust'),
        ('Green', 'Greens & Sages'),
        ('Warm', 'Golds, Ochres & Yellows'),
        ('Black', 'Blacks & Deep Inks'),
        ('Multi', 'Multicolor & Eclectic'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    hex_code = models.CharField(max_length=30, default="#A0987C")
    color_family = models.CharField(max_length=50, choices=FAMILY_CHOICES, default='Neutral')
    is_primary = models.BooleanField(default=True)

    class Meta:
        ordering = ['color_family', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_color_family_display()})"

class Size(models.Model):
    SIZE_TYPE_CHOICES = [
        ('Area Rug', 'Standard Area Rug'),
        ('Runner', 'Hallway & Stair Runner'),
        ('Oversized', 'Mansion & Oversized (10x14+)'),
        ('Round', 'Round & Circular Rug'),
        ('Square', 'Square Rug'),
        ('Swatch', '18" Sample Swatch'),
    ]

    label = models.CharField(max_length=50, unique=True) # e.g. "8'X10'", "9'X12'", "2'6\"X8' Runner"
    slug = models.SlugField(max_length=60, unique=True)
    size_type = models.CharField(max_length=50, choices=SIZE_TYPE_CHOICES, default='Area Rug')
    width_inches = models.PositiveIntegerField(null=True, blank=True)
    length_inches = models.PositiveIntegerField(null=True, blank=True)
    sqft = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'label']

    def save(self, *args, **kwargs):
        if not self.slug:
            clean = self.label.replace('"', '').replace("'", '').replace(' ', '-').lower()
            self.slug = slugify(clean)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.label} ({self.get_size_type_display()})"

class ConstructionType(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g. "Hand Knotted", "Hand Tufted", "Handwoven Flatweave"
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    knot_count_typical = models.CharField(max_length=50, blank=True, default="80-120 KPSI")
    production_lead_weeks = models.PositiveIntegerField(default=12)
    heritage_region = models.CharField(max_length=100, default="Bhadohi, India")

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=120, unique=True) # e.g. "100% Hand-Spun Wool", "Wool & Pure Silk"
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_natural = models.BooleanField(default=True)
    softness_score = models.PositiveSmallIntegerField(default=9) # 1 to 10
    durability_score = models.PositiveSmallIntegerField(default=9) # 1 to 10
    eco_certified = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Style(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g. "Traditional & Oriental", "Modern & Architectural"
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Shape(models.Model):
    name = models.CharField(max_length=50, unique=True) # Rectangle, Runner, Round, Square, Oval
    slug = models.SlugField(max_length=60, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class RoomType(models.Model):
    name = models.CharField(max_length=100, unique=True) # Living Room, Dining Room, Bedroom, Outdoor
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductFeature(models.Model):
    name = models.CharField(max_length=120, unique=True) # e.g. "Performance", "Indoor/Outdoor", "Washables", "Stain Resistant Coating", "Floor Heating Safe", "Rug Pad Recommended"
    slug = models.SlugField(max_length=140, unique=True)
    icon = models.CharField(max_length=60, blank=True, default="ri-checkbox-circle-line")
    description = models.TextField(blank=True)
    is_highlighted = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Product Feature"
        verbose_name_plural = "Product Features"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class MegaMenuItem(models.Model):
    SECTION_CHOICES = [
        ('featured', 'Featured'),
        ('custom', 'Custom'),
        ('one_of_a_kind', 'One of a kind'),
        ('decor', 'Decor Navigation'),
    ]

    section = models.CharField(max_length=50, choices=SECTION_CHOICES, default='featured')
    title = models.CharField(max_length=120)
    url = models.CharField(max_length=255, default='/rugs/')
    badge = models.CharField(max_length=50, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

class MegaMenuColumnConfig(models.Model):
    COLUMN_CHOICES = [
        ('featured', 'Column 1 — Featured'),
        ('color', 'Column 2 — Color'),
        ('material', 'Column 3 — Material'),
        ('construction', 'Column 4 — Construction'),
        ('custom', 'Column 5 — Custom & One of a kind'),
        ('sizes', 'Column 6 — In stock now'),
    ]

    column_key = models.CharField(max_length=50, unique=True, choices=COLUMN_CHOICES)
    display_title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True)
    is_visible = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    # Optional Promotional Banner Card
    promo_banner_active = models.BooleanField(default=False)
    promo_banner_title = models.CharField(max_length=120, blank=True)
    promo_banner_subtitle = models.CharField(max_length=200, blank=True)
    promo_banner_image = models.URLField(max_length=500, blank=True)
    promo_banner_link = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = "Mega Menu Column Config"
        verbose_name_plural = "Mega Menu Column Configs"

    def __str__(self):
        return f"{self.get_column_key_display()} ({self.display_title})"


# ==========================================
# 2. CORE PRODUCT MODEL (ADVANCED RUG ENTITY)


# ==========================================

class Product(models.Model):
    CONSTRUCTION_CHOICES = [
        ('Hand Knotted', 'Hand Knotted'),
        ('Handwoven', 'Handwoven Flatweave'),
        ('Hand Tufted', 'Hand Tufted'),
        ('Power Loomed', 'Power Loomed'),
    ]

    MATERIAL_CHOICES = [
        ('100% Wool', '100% Wool'),
        ('Wool Blend', 'Wool Blend'),
        ('CallaLuxe Acrylic', '100% CallaLuxe Solution-Dyed Acrylic'),
        ('Natural Fibers', 'Natural Fibers / Jute'),
        ('Performance', 'High-Performance Poly'),
        ('Fine Fibers', 'Fine Silk & Wool'),
    ]

    TRAFFIC_CHOICES = [
        ('High', 'High Traffic — Foyer, Living & Commercial'),
        ('Moderate', 'Moderate Traffic — Dining & Family Room'),
        ('Gentle', 'Gentle Luxury — Master Bedroom Only'),
    ]

    # Basic Identification
    name = models.CharField(max_length=200)
    catalog_code = models.CharField(max_length=50, blank=True) # e.g. TRZ05
    slug = models.SlugField(max_length=220, unique=True)
    collection = models.CharField(max_length=100) # Backward-compatible CharField
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    # Advanced Normalized Relational Attributes
    collection_obj = models.ForeignKey(RugCollection, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    designer = models.ForeignKey(Designer, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    primary_material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    construction_type = models.ForeignKey(ConstructionType, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    primary_color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_products')
    accent_colors = models.ManyToManyField(Color, blank=True, related_name='accent_products')
    styles = models.ManyToManyField(Style, blank=True, related_name='products')
    rooms = models.ManyToManyField(RoomType, blank=True, related_name='products')
    shapes = models.ManyToManyField(Shape, blank=True, related_name='products')
    features = models.ManyToManyField(ProductFeature, blank=True, related_name='products')

    # Craftsmanship & Technical Specs
    construction = models.CharField(max_length=50, choices=CONSTRUCTION_CHOICES, default='Handwoven')
    material = models.CharField(max_length=100, choices=MATERIAL_CHOICES, default='CallaLuxe Acrylic')
    origin = models.CharField(max_length=100, default='Rajasthan, India')
    pile_height = models.CharField(max_length=50, default='1/3"')
    pile_thickness_type = models.CharField(max_length=50, blank=True, default='Medium (0.4" - 0.6")')
    knot_count = models.CharField(max_length=60, blank=True, default='80-120 KPSI')
    backing = models.CharField(max_length=100, blank=True, default='Cotton Weft / Canvas')
    traffic_rating = models.CharField(max_length=50, choices=TRAFFIC_CHOICES, default='High')

    # Features & Certifications
    is_outdoor_safe = models.BooleanField(default=False)
    is_floor_heating_safe = models.BooleanField(default=True)
    is_custom_size_available = models.BooleanField(default=True)
    sample_available = models.BooleanField(default=True)
    artisan_days_to_craft = models.PositiveIntegerField(default=120)

    # Content & Media
    description = models.TextField(default="Handcrafted by generational master weavers in Rajasthan, India, this heirloom-quality rug unites centuries-old knotting artistry with contemporary interior elegance. Spun from pure natural fibers with meticulous knot-by-knot precision, each piece embodies the dedication, soulful craft, and human touch of over 40,000 artisan families.")
    care_instructions = models.TextField(default="Vacuum regularly on low-power suction-only setting without a rotating beater bar. Spot clean spills immediately by blotting with a clean, undyed cloth and mild pH-neutral soap. Professional hand immersion rug cleaning recommended every 3-5 years. Rug pad recommended to prevent slipping and extend fiber longevity.")
    image_url = models.URLField(max_length=500)
    secondary_image_url = models.URLField(max_length=500, blank=True)
    lifestyle_image_url = models.URLField(max_length=500, blank=True)
    video_url = models.URLField(max_length=500, blank=True)
    ar_model_url = models.URLField(max_length=500, blank=True) # 3D Augmented Reality Model (USDZ / GLB)

    # Pricing & Flags
    price_from = models.DecimalField(max_digits=10, decimal_places=2, default=1605.00)
    badge = models.CharField(max_length=50, blank=True)
    is_callaluxe = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_in_stock = models.BooleanField(default=True)
    lead_time_days = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/{self.slug}.html"

    def __str__(self):
        return f"{self.name} ({self.catalog_code})"


# ==========================================
# 3. ADVANCED PRODUCT VARIANT (SIZES & PRICING)
# ==========================================

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size_obj = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True, related_name='variants')
    shape = models.ForeignKey(Shape, on_delete=models.SET_NULL, null=True, blank=True, related_name='variants')
    size = models.CharField(max_length=50) # e.g. 18" Swatch, 6'x9', 8'x10', 9'x12', 10'x14', 12'x15'
    color_name = models.CharField(max_length=100, default="Signature Palette")
    color_hex = models.CharField(max_length=20, default="#A0987C")
    sku = models.CharField(max_length=100, blank=True)
    upc_code = models.CharField(max_length=50, blank=True)
    
    # Tiered Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2) # Consumer Price
    trade_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Wholesale Trade Price
    msrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Retail List Price
    
    # Logistics & Inventory
    weight_lbs = models.DecimalField(max_digits=6, decimal_places=2, default=32.00)
    inventory_count = models.PositiveIntegerField(default=10)
    in_stock = models.BooleanField(default=True)
    is_swatch_sample = models.BooleanField(default=False)
    variant_image = models.URLField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        if not self.msrp and self.price:
            self.msrp = (Decimal(str(self.price)) * Decimal('1.30')).quantize(Decimal('0.01'))
        if not self.trade_price and self.price:
            self.trade_price = (Decimal(str(self.price)) * Decimal('0.70')).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.size} (${self.price})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image_url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


# ==========================================
# 4. RUG INDUSTRY CLIENT & TRADE SERVICES
# ==========================================

class SwatchSampleRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Fulfillment'),
        ('Shipped', 'Shipped with Tracking'),
        ('Delivered', 'Delivered to Designer'),
        ('Returned', 'Sample Ring Returned'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='swatch_requests')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    shipping_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=30)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Swatch Request: {self.product.name} for {self.company or self.first_name}"

class CustomerReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author_name = models.CharField(max_length=120)
    author_title = models.CharField(max_length=120, blank=True, default="Verified Interior Designer")
    rating = models.PositiveSmallIntegerField(default=5) # 1 - 5
    title = models.CharField(max_length=200)
    review_body = models.TextField()
    room_photo_url = models.URLField(blank=True, max_length=500)
    is_verified_trade = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review ({self.rating}★) for {self.product.name} by {self.author_name}"

class ProjectList(models.Model):
    """Client presentation boards for interior designers."""
    title = models.CharField(max_length=150) # e.g. "Malibu Coastline - Primary Living Suite"
    designer_name = models.CharField(max_length=120)
    designer_email = models.EmailField()
    client_name = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Project Board: {self.title} ({self.designer_name})"

class ProjectListItem(models.Model):
    project = models.ForeignKey(ProjectList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selected_variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    room_assignment = models.CharField(max_length=100, blank=True, default="Living Room")
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.project.title}"

class CareGuide(models.Model):
    title = models.CharField(max_length=150) # e.g. "Complete Wool Rug Longevity & Stain Removal Guide"
    slug = models.SlugField(max_length=160, unique=True)
    material_target = models.CharField(max_length=100) # e.g. "Pure Wool", "Silk Blend", "CallaLuxe Performance"
    routine_care = models.TextField()
    spill_emergency_protocol = models.TextField()
    professional_cleaning_guidelines = models.TextField()
    video_demonstration_url = models.URLField(blank=True, max_length=500)

    def __str__(self):
        return self.title


# ==========================================
# 5. TRADE APPLICATIONS & SYSTEM MODELS
# ==========================================

class TradeApplication(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    business_type = models.CharField(max_length=100, default='Interior Designer')
    website = models.URLField(blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.first_name} {self.last_name}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class ContactInquiry(models.Model):
    INQUIRY_TYPES = [
        ('general', 'General Customer Inquiries'),
        ('trade', 'Trade Program & Wholesale Pricing'),
        ('order', 'Order Status & Tracking'),
        ('return', 'Returns, Swatch Exchange & RMA'),
        ('custom', 'Custom Bespoke Rug Sizing'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    inquiry_type = models.CharField(max_length=40, choices=INQUIRY_TYPES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.full_name} — {self.subject} ({self.get_inquiry_type_display()})"

class SiteSetting(models.Model):
    # Top Announcement Banner
    announcement_text = models.CharField(max_length=255, default="COMPLIMENTARY SHIPPING ON ORDERS OVER $500 | TRADE PARTNERS RECEIVE EXCLUSIVE PROJECT DISCOUNTS")
    announcement_link_text = models.CharField(max_length=100, default="APPLY FOR TRADE")
    announcement_link_url = models.CharField(max_length=200, default="/become-a-partner/")
    announcement_bg_color = models.CharField(max_length=30, default="#1F1E1C")
    announcement_active = models.BooleanField(default=True)

    # Header & Branding
    site_name = models.CharField(max_length=100, default="AZI HOME")
    header_logo_url = models.URLField(max_length=500, blank=True)
    free_shipping_threshold = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)

    # Hero Showcase
    hero_eyebrow = models.CharField(max_length=100, default="EXCLUSIVE TO AZI HOME")
    hero_title = models.CharField(max_length=200, default="CallaLuxe Performance & The Tierzah Heirloom")
    hero_subtitle = models.TextField(default="Centuries of Indian weaving artistry reimagined with revolutionary solution-dyed fibers and antique floral patinas.")
    hero_cta_primary_text = models.CharField(max_length=50, default="Explore Tierzah TRZ05")
    hero_cta_primary_url = models.CharField(max_length=200, default="/tierzah-trz05.html")
    hero_cta_secondary_text = models.CharField(max_length=50, default="Discover CallaLuxe")
    hero_cta_secondary_url = models.CharField(max_length=200, default="/callaluxe/")
    hero_video_url = models.URLField(max_length=500, blank=True, default="https://player.vimeo.com/video/882894564?background=1&autoplay=1&loop=1&byline=0&title=0&muted=1")

    # Artisan Heritage Section
    heritage_heading = models.CharField(max_length=200, default="40,000 Artisans. One Collective Vision.")
    heritage_description = models.TextField(default="By removing the middleman, AZI HOME empowers women and generational artisans across 600 villages in Bhadohi with living wages, healthcare, and educational dignity.")
    heritage_image_url = models.URLField(max_length=500, default="https://www.jaipurliving.com/media/wysiwyg/2A5A3712-Weavers_1920x600_1.jpg")

    # Brand & Contact Details
    contact_phone = models.CharField(max_length=50, default="+1 (888) 676-7330")
    contact_email = models.EmailField(default="support@azi-home.com")
    trade_email = models.EmailField(default="trade@azi-home.com")
    showroom_address = models.CharField(max_length=255, default="3015 Windward Plaza, Suite 400, Alpharetta, GA 30005")

    # Social Channels & Footer
    instagram_url = models.URLField(blank=True, default="https://instagram.com/azihome")
    pinterest_url = models.URLField(blank=True, default="https://pinterest.com/azihome")
    linkedin_url = models.URLField(blank=True, default="https://linkedin.com/company/azihome")
    youtube_url = models.URLField(blank=True, default="https://youtube.com")
    footer_copyright_text = models.CharField(max_length=255, default="© 2026 AZI HOME Inc. All Rights Reserved. Master Weavers of Bhadohi.")

    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "AZI HOME Site Configuration"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

class PageContent(models.Model):
    PAGE_CHOICES = [
        ('home', 'Homepage — Hero & Highlights'),
        ('story', 'The Story & Artisan Heritage'),
        ('trade', 'Trade Program & Interior Designers'),
        ('contract', 'Contract & Commercial Hospitality'),
        ('callaluxe', 'CallaLuxe Luxury Performance'),
        ('rugs', 'Handcrafted Rugs Catalog'),
        ('decor', 'Luxury Decor & Accents'),
        ('contact', 'Contact Us & Global Showrooms'),
        ('customer_service', 'Customer Service & Concierge'),
        ('privacy', 'Privacy Policy & Data Rights'),
        ('terms', 'Terms & Conditions of Sale'),
        ('refund', 'Refund, Return & Exchange Policy'),
    ]

    page_key = models.CharField(max_length=100, unique=True, choices=PAGE_CHOICES)
    page_name = models.CharField(max_length=200, blank=True)

    # Hero & Header
    eyebrow = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    hero_image = models.URLField(max_length=500, blank=True)
    hero_video_url = models.URLField(max_length=500, blank=True)

    # Call-to-Action Buttons
    cta_primary_text = models.CharField(max_length=100, blank=True)
    cta_primary_url = models.CharField(max_length=255, blank=True)
    cta_secondary_text = models.CharField(max_length=100, blank=True)
    cta_secondary_url = models.CharField(max_length=255, blank=True)

    # Secondary Content Section
    section_heading = models.CharField(max_length=255, blank=True)
    section_subheading = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    secondary_image = models.URLField(max_length=500, blank=True)
    highlight_text = models.TextField(blank=True)

    # Dynamic JSON data for custom page features (e.g. stats, perk lists)
    extra_data = models.JSONField(default=dict, blank=True)

    # SEO Metadata
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page Content"
        verbose_name_plural = "Pages Content"
        ordering = ['page_key']

    def __str__(self):
        return f"{self.get_page_key_display() if hasattr(self, 'get_page_key_display') else self.page_key} ({self.page_key})"

    @classmethod
    def get_page(cls, key, default_data=None):
        obj = cls.objects.filter(page_key=key).first()
        if not obj and default_data:
            obj = cls.objects.create(page_key=key, **default_data)
        return obj


class MediaAsset(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video (MP4 / WebM / MOV)'),
        ('model3d', '3D / AR Model (USDZ / GLB)'),
        ('document', 'Document (PDF / Catalog)'),
        ('other', 'Other Media File'),
    ]

    title = models.CharField(max_length=255, blank=True)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField(max_length=600)
    file_size = models.PositiveIntegerField(default=0) # bytes
    file_type = models.CharField(max_length=30, choices=MEDIA_TYPES, default='image')
    mime_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Media Asset"
        verbose_name_plural = "Media Assets"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()})"

    @property
    def formatted_size(self):
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.2f} MB"
