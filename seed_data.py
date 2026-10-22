import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaipur_project.settings')
django.setup()

from storefront.models import Category, Product, ProductVariant, ProductImage

def seed():
    print("Clearing old data...")
    ProductImage.objects.all().delete()
    ProductVariant.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()

    print("Creating categories...")
    rugs_cat = Category.objects.create(
        name="Rugs",
        slug="rugs",
        description="Handcrafted luxury rugs woven by master artisans in India.",
        image_url="https://www.jaipurliving.com/media/catalog/category/Rugs_Nav_Feat_Image.jpg"
    )
    callaluxe_cat = Category.objects.create(
        name="CallaLuxe",
        slug="callaluxe",
        description="Luxury performance rugs crafted with solution-dyed acrylic fibers.",
        image_url="https://www.jaipurliving.com/media/catalog/category/CFL103_mm_feat.jpg"
    )
    decor_cat = Category.objects.create(
        name="Decor",
        slug="decor",
        description="Artisanal pillows, poufs, and luxury handwoven throws.",
        image_url="https://www.jaipurliving.com/media/catalog/category/shop-all-meganav-july.jpg"
    )

    sizes_and_multipliers = [
        ("18\" Swatch", Decimal('25.00')),
        ("3'X10' Runner", Decimal('980.00')),
        ("6'X9'", Decimal('1605.00')),
        ("8'X10'", Decimal('2380.00')),
        ("9'X12'", Decimal('3690.00')),
        ("10'X14'", Decimal('4785.00')),
        ("12'X15'", Decimal('6255.00')),
    ]

    print("Creating CallaLuxe Products...")
    # CNL104
    p104 = Product.objects.create(
        name="Canyon 01 CNL104",
        catalog_code="CNL104",
        slug="canyon-01-cnl104",
        collection="Canyon 01",
        category=callaluxe_cat,
        construction="Handwoven",
        material="CallaLuxe Acrylic",
        origin="Bhadohi, India",
        pile_height="1/3\"",
        description="CallaLuxe by AZI HOME defines the new standard in luxury performance rugs. Innovative yarn construction delivers the high end softness and texture of wool with the resilience of performance. Echoing the enduring beauty of sculpted landscapes, the Korleth design marries organic elegance with innovative performance. These textured solids are a hand-woven flatweave construction, a technique carried forward by artisans in Bhadohi for generations.",
        image_url="https://www.jaipurliving.com/media/catalog/product/C/N/CNL104.jpg?quality=70&bg-color=255,255,255&fit=bounds&height=700&width=500&canvas=500:700",
        secondary_image_url="https://www.jaipurliving.com/media/wysiwyg/LS_Grid_Graphic_Website_1_.png",
        lifestyle_image_url="https://www.jaipurliving.com/media/catalog/product/C/N/CNL104.jpg",
        price_from=Decimal('1605.00'),
        badge="CallaLuxe Exclusive",
        is_callaluxe=True,
        is_trending=True,
        is_in_stock=True,
    )
    for size, price in sizes_and_multipliers:
        ProductVariant.objects.create(
            product=p104,
            size=size,
            color_name="Slate Green & Elmwood",
            color_hex="#A0987C",
            sku=f"CNL104-{size.replace(' ', '')}",
            price=price,
        )

    # CNL101
    p101 = Product.objects.create(
        name="Canyon 01 CNL101",
        catalog_code="CNL101",
        slug="canyon-01-cnl101",
        collection="Canyon 01",
        category=callaluxe_cat,
        construction="Handwoven",
        material="CallaLuxe Acrylic",
        origin="Bhadohi, India",
        pile_height="1/3\"",
        description="Dove and Turtledove tones woven in an exquisite low-profile flatweave. Built for the high-traffic luxury rooms that get used hardest, crafted with solution-dyed acrylic fibers exclusively engineered for AZI HOME. Full saturation holds year after year without fading.",
        image_url="https://www.jaipurliving.com/media/catalog/product//M/J/MJL01.jpg",
        secondary_image_url="https://www.jaipurliving.com/media/wysiwyg/SAG_swatches_CYC_RCT_2__26_1_1__1.jpg",
        price_from=Decimal('1605.00'),
        badge="Best Seller",
        is_callaluxe=True,
        is_trending=True,
        is_in_stock=True,
    )
    for size, price in sizes_and_multipliers:
        ProductVariant.objects.create(
            product=p101,
            size=size,
            color_name="Oatmeal & Dove",
            color_hex="#CBC3B4",
            sku=f"CNL101-{size.replace(' ', '')}",
            price=price,
        )

    # CNL102
    p102 = Product.objects.create(
        name="Canyon 01 CNL102",
        catalog_code="CNL102",
        slug="canyon-01-cnl102",
        collection="Canyon 01",
        category=callaluxe_cat,
        construction="Handwoven",
        material="CallaLuxe Acrylic",
        origin="Bhadohi, India",
        pile_height="1/3\"",
        description="Warm terracotta and clay undertones provide grounding warmth and sophisticated texture. Unyielding performance combined with soft tactile elegance.",
        image_url="https://www.jaipurliving.com/media/catalog/category/CFL103_mm_feat.jpg",
        price_from=Decimal('1605.00'),
        badge="New Arrival",
        is_callaluxe=True,
        is_trending=False,
        is_in_stock=True,
    )
    for size, price in sizes_and_multipliers:
        ProductVariant.objects.create(
            product=p102,
            size=size,
            color_name="Warm Earth Rust",
            color_hex="#8C4E41",
            sku=f"CNL102-{size.replace(' ', '')}",
            price=price,
        )

    # CNL103
    p103 = Product.objects.create(
        name="Canyon 01 CNL103",
        catalog_code="CNL103",
        slug="canyon-01-cnl103",
        collection="Canyon 01",
        category=callaluxe_cat,
        construction="Handwoven",
        material="CallaLuxe Acrylic",
        origin="Bhadohi, India",
        pile_height="1/3\"",
        description="Desert sand and soft alabaster fibers interlock seamlessly in a subtle ribbed texture. Stain-resistant, kid and pet friendly, designed for enduring family life.",
        image_url="https://www.jaipurliving.com/media/catalog/category/CFL209_mm_feat.jpg",
        price_from=Decimal('1605.00'),
        badge="CallaLuxe Exclusive",
        is_callaluxe=True,
        is_trending=False,
        is_in_stock=True,
    )
    for size, price in sizes_and_multipliers:
        ProductVariant.objects.create(
            product=p103,
            size=size,
            color_name="Desert Sand",
            color_hex="#C2B59B",
            sku=f"CNL103-{size.replace(' ', '')}",
            price=price,
        )

    print("Creating Majnun Collection...")
    majnun_items = [
        ("Majnun MJL01", "MJL01", "majnun-mjl01", Decimal('1450.00'), "https://www.jaipurliving.com/media/catalog/product//M/J/MJL01.jpg", "Terracotta & Navy"),
        ("Majnun MJL02", "MJL02", "majnun-mjl02", Decimal('1620.00'), "https://www.jaipurliving.com/media/catalog/product//M/J/MJL02.jpg", "Antique Indigo"),
        ("Majnun MJL03", "MJL03", "majnun-mjl03", Decimal('1890.00'), "https://www.jaipurliving.com/media/catalog/product//m/j/mjl03.jpg", "Sage & Sand"),
        ("Majnun MJL04", "MJL04", "majnun-mjl04", Decimal('2100.00'), "https://www.jaipurliving.com/media/catalog/product//m/j/mjl04.jpg", "Muted Rose Wash"),
        ("Majnun MJL05", "MJL05", "majnun-mjl05", Decimal('1750.00'), "https://www.jaipurliving.com/media/catalog/product//M/J/MJL05.jpg", "Warm Charcoal Bronze"),
    ]

    for name, code, slug, price, img, col in majnun_items:
        prod = Product.objects.create(
            name=name,
            catalog_code=code,
            slug=slug,
            collection="Majnun",
            category=rugs_cat,
            construction="Hand Knotted",
            material="100% Wool",
            origin="Bhadohi, India",
            pile_height="1/2\"",
            description=f"The {name} embodies centuries-old knotting traditions. Spun from pure natural wool and washed to antique perfection, featuring balanced tribal geometry and heirloom elegance.",
            image_url=img,
            lifestyle_image_url="https://mcstaging.jaipurliving.com/media/tmp/product-image-media/slider/Majnun_Banner_2.jpg",
            price_from=price,
            badge="Shoppable Look",
            is_callaluxe=False,
            is_trending=True,
            is_in_stock=True,
        )
        for size, mult in [("6'X9'", price), ("8'X10'", price * Decimal('1.4')), ("9'X12'", price * Decimal('1.85')), ("10'X14'", price * Decimal('2.4'))]:
            ProductVariant.objects.create(
                product=prod,
                size=size,
                color_name=col,
                color_hex="#8A5A44",
                sku=f"{code}-{size.replace(' ', '')}",
                price=mult.quantize(Decimal('1.00')),
            )

    print("Creating Tierzah Collection (TRZ05 & TRZ04)...")
    p_trz05 = Product.objects.create(
        name="Tierzah Rug TRZ05",
        catalog_code="TRZ05",
        slug="tierzah-trz05",
        collection="Tierzah",
        category=rugs_cat,
        construction="Hand Knotted",
        material="100% Wool",
        origin="Bhadohi, India",
        pile_height="1/2\"",
        description="Made of 100% hand knotted wool, this area rug from the Tierzah collection boasts an intricate, floral trellis and border pattern in muted gold and gray. Masterfully woven by skilled artisans in India, the lustrous patina of natural handspun wool brings enduring warmth and timeless heritage elegance to refined interiors.",
        care_instructions="Vacuum regularly with suction only (disengage beater brush). Blot spills immediately with a clean, dry undyed cloth. Professional rug cleaning is recommended. Shedding of loose fibers is normal for new wool rugs and will diminish over time.",
        image_url="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_NSTA25.jpg",
        secondary_image_url="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_2_NSTA25.jpg",
        lifestyle_image_url="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_LS.jpg",
        price_from=Decimal('25.00'),
        badge="Hand Knotted Heirloom",
        is_callaluxe=False,
        is_trending=True,
        is_in_stock=True,
    )

    gallery_trz05 = [
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_NSTA25.jpg", "Tierzah TRZ05 Overhead View", 1),
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_2_NSTA25.jpg", "Tierzah TRZ05 Angle & Pile Texture", 2),
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_3_NSTA25.jpg", "Tierzah TRZ05 Corner & Floral Border", 3),
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_4_NSTA25.jpg", "Tierzah TRZ05 Fringe Detail", 4),
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_LS.jpg", "Tierzah TRZ05 Living Room Scene", 5),
    ]

    for img_url, alt, ord_num in gallery_trz05:
        ProductImage.objects.create(product=p_trz05, image_url=img_url, alt_text=alt, order=ord_num)

    trz_sizes_prices = [
        ("18\" Swatch", Decimal('25.00')),
        ("2'6\"X8' Runner", Decimal('1280.00')),
        ("6'X9'", Decimal('3695.00')),
        ("8'X10'", Decimal('5470.00')),
        ("9'X12'", Decimal('8490.00')),
        ("10'X14'", Decimal('10995.00')),
    ]

    for size, price in trz_sizes_prices:
        ProductVariant.objects.create(
            product=p_trz05,
            size=size,
            color_name="Muted Gold & Gray / Ivory (TRZ05)",
            color_hex="#C2B79B",
            sku=f"TRZ05-{size.replace(' ', '').replace('\"', '').replace('\'', '')}",
            price=price,
            variant_image="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_NSTA25.jpg"
        )
        ProductVariant.objects.create(
            product=p_trz05,
            size=size,
            color_name="Alabaster & Sage / Taupe (TRZ04)",
            color_hex="#9D9B8B",
            sku=f"TRZ04-{size.replace(' ', '').replace('\"', '').replace('\'', '')}",
            price=price,
            variant_image="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_NSTA25.jpg"
        )

    print("Creating Trending & Featured Rugs...")
    trending_items = [
        ("Azad AZA01", "AZA01", "azad-aza01", "Azad", Decimal('2450.00'), "https://www.jaipurliving.com/media/catalog/product//A/Z/AZA01_NSTA25.jpg", "Hand Knotted", "100% Wool", "Turkish Sun-Fade"),
        ("Eden EDE08", "EDE08", "eden-ede08", "Eden", Decimal('3200.00'), "https://www.jaipurliving.com/media/catalog/product//E/D/EDE08_NSTA2026.jpg", "Hand Knotted", "Fine Fibers", "Botanical Garden"),
        ("Elaida ELA03", "ELA03", "elaida-ela03", "Elaida", Decimal('2150.00'), "https://www.jaipurliving.com/media/catalog/product//E/L/ELA03_NSTA25.jpg", "Hand Tufted", "Wool Blend", "Modern Minimalist"),
        ("Cicek CIC02", "CIC02", "cicek-cic02", "Cicek", Decimal('2850.00'), "https://www.jaipurliving.com/media/catalog/product//C/I/CIC02.jpg", "Handwoven", "Natural Fibers", "Organic Texture"),
        ("Vern Yip Signature VYP04", "VYP04", "vern-yip-vyp04", "Vern Yip", Decimal('1980.00'), "https://www.jaipurliving.com/media/wysiwyg/Vern_Yip_3UP.jpg", "Power Loomed", "Performance", "Designer Palette"),
        ("Coastal Breeze CMB07", "CMB07", "coastal-breeze-cmb07", "Coastal", Decimal('1120.00'), "https://www.jaipurliving.com/media/wysiwyg/CMB07_RUG164911_RCT_LS020_1_.jpg", "Power Loomed", "Performance", "In Stock Special"),
    ]

    for name, code, slug, coll, price, img, const, mat, badge in trending_items:
        prod = Product.objects.create(
            name=name,
            catalog_code=code,
            slug=slug,
            collection=coll,
            category=rugs_cat,
            construction=const,
            material=mat,
            origin="Bhadohi, India",
            pile_height="1/3\"",
            description=f"Part of the acclaimed {coll} collection. Masterfully composed with curated dyes and tactile richness, bringing authentic global artisan spirit into the contemporary interior.",
            image_url=img,
            price_from=price,
            badge=badge,
            is_callaluxe=False,
            is_trending=True,
            is_in_stock=True,
        )
        for size, mult in [("6'X9'", price), ("8'X10'", price * Decimal('1.35')), ("9'X12'", price * Decimal('1.78'))]:
            ProductVariant.objects.create(
                product=prod,
                size=size,
                color_name="Artisan Dye",
                color_hex="#948B7E",
                sku=f"{code}-{size.replace(' ', '')}",
                price=mult.quantize(Decimal('1.00')),
            )

    print("Creating Decor Products...")
    decor_items = [
        ("Enkay Embroidered Wool Pillow", "DEC-PLW01", "enkay-embroidered-wool-pillow", Decimal('145.00'), "https://www.jaipurliving.com/media/catalog/category/shop-all-meganav-july.jpg", "Pillows"),
        ("Jaipur Braided Jute Pouf", "DEC-POUF01", "jaipur-braided-jute-pouf", Decimal('220.00'), "https://www.jaipurliving.com/media/catalog/category/19-0053-New_Website_Image-Dropdown-Poufs_1.jpg", "Poufs"),
        ("Handwoven Artisan Alpaca Throw", "DEC-THR01", "handwoven-artisan-alpaca-throw", Decimal('180.00'), "https://www.jaipurliving.com/media/catalog/category/feaured23-compressor_1.jpg", "Throws"),
    ]

    for name, code, slug, price, img, coll in decor_items:
        prod = Product.objects.create(
            name=name,
            catalog_code=code,
            slug=slug,
            collection=coll,
            category=decor_cat,
            construction="Handcrafted",
            material="Natural Fibers",
            origin="Bhadohi, India",
            pile_height="Decorative",
            description=f"Luxury artisan home accessory handmade in Bhadohi with heirloom techniques. Designed to layer texture and refined warmth in any living room or bedroom sanctuary.",
            image_url=img,
            price_from=price,
            badge="Artisan Crafted",
            is_callaluxe=False,
            is_trending=False,
            is_in_stock=True,
        )
        ProductVariant.objects.create(
            product=prod,
            size="Standard",
            color_name="Natural Heritage",
            color_hex="#C5BAA9",
            sku=f"{code}-STD",
            price=price,
        )

    print("Seed complete! Total products:", Product.objects.count())

if __name__ == '__main__':
    seed()
