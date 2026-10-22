import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaipur_project.settings')

import django
django.setup()

from storefront.models import (
    Category, Product, ProductVariant, RugCollection, Designer, Color, Size,
    ConstructionType, Material, Style, Shape, RoomType, SwatchSampleRequest, CustomerReview, CareGuide
)

def run():
    print("Seeding advanced rug taxonomy...")

    # 1. Colors
    colors_data = [
        ("Midnight Blue", "#1A2E40", "Blue"),
        ("Ocean Teal", "#2F6872", "Blue"),
        ("Slate & Mineral", "#6F7D8C", "Blue"),
        ("Ivory / Alabaster", "#F4F1EA", "Neutral"),
        ("Warm Sand", "#D6C7AE", "Neutral"),
        ("Terracotta & Clay", "#B85C46", "Earth"),
        ("Rust & Ochre", "#9C4E38", "Earth"),
        ("Olive & Sage", "#667055", "Green"),
        ("Forest Moss", "#3B4A34", "Green"),
        ("Charcoal & Ash", "#33373B", "Gray"),
        ("Pewter Gray", "#787C80", "Gray"),
        ("Onyx Black", "#151618", "Black"),
        ("Antique Gold", "#C8A155", "Warm"),
    ]
    color_objs = {}
    for name, hex_val, fam in colors_data:
        c, _ = Color.objects.get_or_create(
            name=name,
            defaults={'hex_code': hex_val, 'color_family': fam}
        )
        color_objs[name] = c
    print(f"  + Seeded {len(color_objs)} Colors")

    # 2. Standard Sizes
    sizes_data = [
        ('18" Swatch', 'Swatch', 18, 18, 2.25, 1),
        ("2'X3'", 'Area Rug', 24, 36, 6.00, 2),
        ("2'6\"X8' Runner", 'Runner', 30, 96, 20.00, 3),
        ("2'6\"X12' Long Runner", 'Runner', 30, 144, 30.00, 4),
        ("5'X7'6\"", 'Area Rug', 60, 90, 37.50, 5),
        ("6'X9'", 'Area Rug', 72, 108, 54.00, 6),
        ("8'X10'", 'Area Rug', 96, 120, 80.00, 7),
        ("9'X12'", 'Area Rug', 108, 144, 108.00, 8),
        ("10'X14'", 'Oversized', 120, 168, 140.00, 9),
        ("12'X15'", 'Oversized', 144, 180, 180.00, 10),
        ("8' Round", 'Round', 96, 96, 50.26, 11),
    ]
    size_objs = {}
    for label, stype, w, l, sq, sort in sizes_data:
        s, _ = Size.objects.get_or_create(
            label=label,
            defaults={'size_type': stype, 'width_inches': w, 'length_inches': l, 'sqft': sq, 'sort_order': sort}
        )
        size_objs[label] = s
    print(f"  + Seeded {len(size_objs)} Standard Rug Sizes")

    # 3. Construction Types
    constructions = [
        ("Hand Knotted", "Crafted entirely by hand knot by knot on vertical looms in Rajasthan. Generational heirloom quality.", "80-140 KPSI", 16),
        ("Hand Tufted", "Hand-tufted with tufting guns through a stretched cotton canvas, sheared and latex backed.", "Tufted 45-60 Lbs", 6),
        ("Handwoven Flatweave", "Interlocking warp and weft flatweave with zero pile, reversible and ultra-durable.", "Flat / Dhurrie Weave", 8),
        ("Power Loomed", "Precision architectural weaving engineered on high-speed electronic Wilton looms.", "Machine Precision", 2),
    ]
    const_objs = {}
    for name, desc, kpsi, lead in constructions:
        ct, _ = ConstructionType.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'knot_count_typical': kpsi, 'production_lead_weeks': lead}
        )
        const_objs[name] = ct
    print(f"  + Seeded {len(const_objs)} Construction Types")

    # 4. Materials
    materials = [
        ("100% Hand-Spun Wool", "Unadulterated high-mountain New Zealand and Bikaner wool spun by hand. Rich in natural lanolin stain resistance.", True, 9, 10),
        ("Wool & Mulberry Silk Blend", "Luminous pure mulberry silk blended with wool for an ethereal luster that shifts dynamically with room light.", True, 10, 8),
        ("CallaLuxe Performance Acrylic", "Revolutionary solution-dyed acrylic yarn that withstands direct bleach, red wine, and heavy commercial foot traffic.", False, 8, 10),
        ("Natural Jute & Sisal", "Raw, organic hand-spun plant fibers celebrating earthy unrefined textures.", True, 6, 9),
    ]
    mat_objs = {}
    for name, desc, nat, soft, dur in materials:
        m, _ = Material.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'is_natural': nat, 'softness_score': soft, 'durability_score': dur}
        )
        mat_objs[name] = m
    print(f"  + Seeded {len(mat_objs)} Materials")

    # 5. Styles
    styles = [
        "Traditional & Persian",
        "Modern Architectural",
        "Transitional",
        "Vintage Oushak & Antique Wash",
        "Biophilic & Organic",
        "Minimalist Scandinavian",
        "Geometric & Linear",
    ]
    style_objs = {}
    for st in styles:
        s, _ = Style.objects.get_or_create(name=st)
        style_objs[st] = s
    print(f"  + Seeded {len(style_objs)} Styles")

    # 6. Shapes
    shapes = ["Rectangle", "Runner", "Round", "Square", "Oval"]
    shape_objs = {}
    for sh in shapes:
        shp, _ = Shape.objects.get_or_create(name=sh)
        shape_objs[sh] = shp
    print(f"  + Seeded {len(shape_objs)} Shapes")

    # 7. Rooms
    rooms = [
        ("Living Room", "Large gathering areas requiring plush comfort and high-traffic durability."),
        ("Dining Room", "Smooth low-pile or flatweave for easy chair gliding and spill resistance."),
        ("Bedroom & Suite", "Ultimate softness underfoot, deep pile and luxurious silk blends."),
        ("Hallway & Entry", "Sturdy high-density runners and stain-shielded entrance pieces."),
        ("Outdoor Patio", "UV-resistant and waterproof solution-dyed fibers."),
        ("Contract & Hospitality", "Commercial grade durability testing and ASTM flame certification."),
    ]
    room_objs = {}
    for r_name, r_desc in rooms:
        rm, _ = RoomType.objects.get_or_create(name=r_name, defaults={'description': r_desc})
        room_objs[r_name] = rm
    print(f"  + Seeded {len(room_objs)} Room Types")

    # 8. Designers
    designers_data = [
        ("Vern Yip", "HGTV star & acclaimed architectural interior designer celebrating crisp symmetry and clean living.", "https://www.jaipurliving.com/media/wysiwyg/Vern_Yip_3UP.jpg"),
        ("Jennifer Adams", "Award-winning luxury lifestyle author and bedding/rug designer focused on effortless tranquility.", "https://www.jaipurliving.com/media/wysiwyg/JA_Designer_Banner.jpg"),
        ("Jaipur Rugs Heritage Collective", "Master female weavers of Rajasthan carrying on 400-year-old Mughal knotting traditions.", "https://www.jaipurliving.com/media/wysiwyg/2A5A3712-Weavers_1920x600_1.jpg"),
    ]
    designer_objs = {}
    for d_name, d_bio, d_img in designers_data:
        ds, _ = Designer.objects.get_or_create(
            name=d_name,
            defaults={'bio': d_bio, 'portrait_image': d_img, 'is_featured': True}
        )
        designer_objs[d_name] = ds
    print(f"  + Seeded {len(designer_objs)} Designers")

    # 9. Collections
    collections_data = [
        ("Tierzah", "Timeless Persian heritage floral medallions hand-knotted in 100% pure wool with antique tea-washed patinas.", "https://www.jaipurliving.com/media/catalog/product/t/r/trz05_rug168395_rct_wav.jpg", "Jaipur Rugs Heritage Collective"),
        ("CallaLuxe", "The pinnacle of indoor/outdoor performance luxury—softness of cashmere with bleach-cleanable endurance.", "https://www.jaipurliving.com/media/catalog/category/CFL103_mm_feat.jpg", "Vern Yip"),
        ("Salinas", "Southwestern adobe and Nordic geometric line work rendered in plush textured wool blends.", "https://www.jaipurliving.com/media/catalog/product/s/l/sln01_rug168001_rct_wav.jpg", "Jennifer Adams"),
        ("Cirque", "High-low sheared dimensional viscose and wool evocative of modern museum modernism.", "https://www.jaipurliving.com/media/catalog/product/c/i/crq01_rug168002_rct_wav.jpg", "Jaipur Rugs Heritage Collective"),
        ("Mythos", "Hand-tufted Greek key and classical architectural motifs in balanced mineral hues.", "https://www.jaipurliving.com/media/catalog/product/m/y/myt01_rug168003_rct_wav.jpg", "Vern Yip"),
    ]
    col_objs = {}
    for c_name, c_desc, c_img, des_name in collections_data:
        rc, _ = RugCollection.objects.get_or_create(
            name=c_name,
            defaults={
                'description': c_desc,
                'hero_image': c_img,
                'designer': designer_objs.get(des_name),
                'is_featured': True
            }
        )
        col_objs[c_name] = rc
    print(f"  + Seeded {len(col_objs)} Rug Collections")

    # 10. Link existing products to the new entities
    for p in Product.objects.all():
        if p.collection in col_objs:
            p.collection_obj = col_objs[p.collection]
        
        if p.construction in const_objs:
            p.construction_type = const_objs[p.construction]
        else:
            p.construction_type = const_objs.get("Hand Knotted")

        if "Wool" in p.material:
            p.primary_material = mat_objs.get("100% Hand-Spun Wool")
        elif "CallaLuxe" in p.material:
            p.primary_material = mat_objs.get("CallaLuxe Performance Acrylic")
        else:
            p.primary_material = mat_objs.get("100% Hand-Spun Wool")

        if "Blue" in p.name or "Slate" in p.name:
            p.primary_color = color_objs.get("Midnight Blue")
        elif "Ivory" in p.name or "Beige" in p.name or "Cream" in p.name:
            p.primary_color = color_objs.get("Ivory / Alabaster")
        elif "Terra" in p.name or "Rust" in p.name:
            p.primary_color = color_objs.get("Terracotta & Clay")
        else:
            p.primary_color = color_objs.get("Warm Sand")

        p.save()
        p.styles.set([style_objs["Traditional & Persian"], style_objs["Transitional"]])
        p.rooms.set([room_objs["Living Room"], room_objs["Dining Room"], room_objs["Bedroom & Suite"]])
        p.shapes.set([shape_objs["Rectangle"], shape_objs["Runner"]])

    print("  + Linked all existing Products to new Relational Taxonomy Entities")

    # 11. Swatch Samples Request Seed
    sample_prod = Product.objects.filter(catalog_code="TRZ05").first() or Product.objects.first()
    if sample_prod:
        sample_var = sample_prod.variants.filter(size__icontains="Swatch").first() or sample_prod.variants.first()
        SwatchSampleRequest.objects.get_or_create(
            product=sample_prod,
            email="sarah.jenkins@studiojinteriors.com",
            defaults={
                'variant': sample_var,
                'first_name': "Sarah",
                'last_name': "Jenkins",
                'company': "Studio J Interiors & Architecture",
                'phone': "+1 (415) 890-2341",
                'shipping_address': "450 Sutter St, Suite 1200",
                'city': "San Francisco",
                'state': "CA",
                'postal_code': "94108",
                'status': "Shipped",
                'tracking_number': "1Z9999999999999999"
            }
        )
        print("  + Seeded SwatchSampleRequest")

    # 12. Customer Reviews Seed
    if sample_prod:
        CustomerReview.objects.get_or_create(
            product=sample_prod,
            author_name="Marcus Vance, ASID",
            defaults={
                'author_title': "Principal Architect at Vance Design Group",
                'rating': 5,
                'title': "Breathtaking depth of color and unmatched knotting density",
                'review_body': "Specified the 10'X14' Tierzah for a primary penthouse living room in Aspen. The hand-spun wool has an incredible antique luster that changes delicately between daytime and evening fireside lighting. Truly one of the finest rugs Jaipur Living has ever produced.",
                'room_photo_url': "https://www.jaipurliving.com/media/wysiwyg/2A5A3712-Weavers_1920x600_1.jpg",
                'is_verified_trade': True,
                'is_approved': True
            }
        )
        print("  + Seeded CustomerReview")

    # 13. Care Guide Seed
    CareGuide.objects.get_or_create(
        slug="wool-rug-care-and-stain-removal",
        defaults={
            'title': "Pure Wool Rug Preservation & Emergency Stain Protocol",
            'material_target': "100% Hand-Spun Wool",
            'routine_care': "Vacuum 1-2 times weekly on suction-only setting without a rotating beater bar. Rotate the rug 180 degrees every six months to ensure even wear patterns.",
            'spill_emergency_protocol': "Blot immediately with a clean, dry white cotton cloth. Never rub vigorously. For wine or coffee, use lukewarm water with a small amount of mild pH-neutral wool cleanser. Work from the outside of the stain inward.",
            'professional_cleaning_guidelines': "Professional hand-washing immersion rug cleaning recommended every 3-5 years by an Oriental Rug specialist."
        }
    )
    print("  + Seeded CareGuide")

    print("\nAdvanced taxonomy & models successfully seeded!")

if __name__ == '__main__':
    run()
