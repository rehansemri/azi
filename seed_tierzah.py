import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaipur_project.settings')
django.setup()

from storefront.models import Category, Product, ProductVariant, ProductImage

def run():
    rugs_cat, _ = Category.objects.get_or_create(
        slug="rugs",
        defaults={
            "name": "Rugs",
            "description": "Handcrafted luxury rugs woven by master artisans in India.",
            "image_url": "https://www.jaipurliving.com/media/catalog/category/Rugs_Nav_Feat_Image.jpg"
        }
    )

    # Delete existing Tierzah if any
    Product.objects.filter(slug__in=["tierzah-trz05", "tierzah-trz04"]).delete()

    print("Seeding Tierzah TRZ05...")
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
        ProductImage.objects.create(
            product=p_trz05,
            image_url=img_url,
            alt_text=alt,
            order=ord_num
        )

    trz_sizes_prices = [
        ("18\" Swatch", Decimal('25.00')),
        ("2'6\"X8' Runner", Decimal('1280.00')),
        ("6'X9'", Decimal('3695.00')),
        ("8'X10'", Decimal('5470.00')),
        ("9'X12'", Decimal('8490.00')),
        ("10'X14'", Decimal('10995.00')),
    ]

    # Variants for TRZ05
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

    # Colorway TRZ04 as well on TRZ05 product
    for size, price in trz_sizes_prices:
        ProductVariant.objects.create(
            product=p_trz05,
            size=size,
            color_name="Alabaster & Sage / Taupe (TRZ04)",
            color_hex="#9D9B8B",
            sku=f"TRZ04-{size.replace(' ', '').replace('\"', '').replace('\'', '')}",
            price=price,
            variant_image="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_NSTA25.jpg"
        )

    # Also create standalone TRZ04 for direct navigation if clicked
    p_trz04 = Product.objects.create(
        name="Tierzah Rug TRZ04",
        catalog_code="TRZ04",
        slug="tierzah-trz04",
        collection="Tierzah",
        category=rugs_cat,
        construction="Hand Knotted",
        material="100% Wool",
        origin="Bhadohi, India",
        pile_height="1/2\"",
        description="Made of 100% hand knotted wool, this area rug from the Tierzah collection features a soothing botanical trellis motif in soft alabaster, muted sage, and antique taupe.",
        care_instructions="Vacuum regularly with suction only. Spot clean with mild detergent. Professional cleaning recommended.",
        image_url="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_NSTA25.jpg",
        secondary_image_url="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_2_NSTA25.jpg",
        lifestyle_image_url="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_LS.jpg",
        price_from=Decimal('25.00'),
        badge="Hand Knotted Heirloom",
        is_callaluxe=False,
        is_trending=True,
        is_in_stock=True,
    )

    gallery_trz04 = [
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_NSTA25.jpg", "Tierzah TRZ04 Overhead View", 1),
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_2_NSTA25.jpg", "Tierzah TRZ04 Texture Angle", 2),
        ("https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_3_NSTA25.jpg", "Tierzah TRZ04 Border Detail", 3),
    ]
    for img_url, alt, ord_num in gallery_trz04:
        ProductImage.objects.create(product=p_trz04, image_url=img_url, alt_text=alt, order=ord_num)

    for size, price in trz_sizes_prices:
        ProductVariant.objects.create(
            product=p_trz04,
            size=size,
            color_name="Alabaster & Sage / Taupe (TRZ04)",
            color_hex="#9D9B8B",
            sku=f"TRZ04-{size.replace(' ', '').replace('\"', '').replace('\'', '')}",
            price=price,
            variant_image="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ04_NSTA25.jpg"
        )
        ProductVariant.objects.create(
            product=p_trz04,
            size=size,
            color_name="Muted Gold & Gray / Ivory (TRZ05)",
            color_hex="#C2B79B",
            sku=f"TRZ05-{size.replace(' ', '').replace('\"', '').replace('\'', '')}",
            price=price,
            variant_image="https://www.jaipurliving.com/media/catalog/product/T/R/TRZ05_NSTA25.jpg"
        )

    print("Tierzah rugs seeded successfully!")

if __name__ == '__main__':
    run()
