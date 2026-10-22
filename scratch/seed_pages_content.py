import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaipur_project.settings')
django.setup()

from storefront.models import PageContent

PAGES_DATA = [
    {
        'page_key': 'home',
        'page_name': 'Homepage — Hero & Highlights',
        'eyebrow': 'LUXURY RUGS, MADE FOR REAL LIFE',
        'title': 'CallaLuxe & The Tierzah Heirloom',
        'subtitle': 'Softness of wool. Resilience of performance. Crafted with solution-dyed acrylic fibers and antique floral patinas exclusively engineered for Jaipur Living.',
        'hero_image': 'https://www.jaipurliving.com/media/wysiwyg/LS_Grid_Graphic_Website_1_.png',
        'hero_video_url': 'https://player.vimeo.com/video/1226077355?background=1&autoplay=1&loop=1&muted=1&autopause=0&playsinline=1&dnt=1',
        'cta_primary_text': 'Shop CallaLuxe',
        'cta_primary_url': '/callaluxe/',
        'cta_secondary_text': 'Explore All Rugs',
        'cta_secondary_url': '/rugs/',
        'section_heading': 'ESTABLISHED 1978 • JAIPUR, INDIA',
        'section_subheading': 'One Collective Purpose',
        'highlight_text': 'Since 1978, Jaipur Living has redefined rug making—where the value lies not just in the rugs themselves, but in the hands that create them. Every piece is a reflection of heritage, care, and craftsmanship passed down through generations of artisans straight to you.',
        'body': 'By removing the middleman, Jaipur Living empowers women and generational artisans across 600 villages in Rajasthan with living wages, healthcare, and educational dignity.',
        'secondary_image': 'https://www.jaipurliving.com/media/wysiwyg/2A5A3712-Weavers_1920x600_1.jpg',
        'meta_title': 'Jaipur Living | Shop Luxurious Handmade Rugs + Decor',
        'meta_description': 'Discover museum-grade handcrafted rugs woven knot by knot in Rajasthan, India. Shop CallaLuxe luxury performance rugs and heirloom designs.',
    },
    {
        'page_key': 'story',
        'page_name': 'The Story & Artisan Craftsmanship',
        'eyebrow': 'A PURPOSE-DRIVEN JOURNEY',
        'title': 'The Jaipur Living Story',
        'subtitle': 'Connecting people through handmade beauty since 1978. Rooted in social impact and ancestral craft.',
        'hero_image': 'https://www.jaipurliving.com/media/wysiwyg/2A5A3712-Weavers_1920x600_1.jpg',
        'highlight_text': '“A rug isn’t just an interior object—it carries the heartbeat, dreams, and dignity of the artisan family whose hands tied every single knot.”',
        'section_heading': 'Founded on Dignity & Craft',
        'section_subheading': 'Generational Weavers Across 600 Villages',
        'body': 'In 1978, N.K. Chaudhary founded Jaipur Rugs with two looms and nine artisans. Rejecting predatory middlemen, he created an unprecedented grassroots network that directly empowered rural women and hereditary weavers across Rajasthan, India.\n\nToday, Jaipur Living continues this legacy under daughter Asha Chaudhary’s leadership in Atlanta, bringing museum-grade handmade luxury to premier interior designers and architectural projects worldwide.',
        'secondary_image': 'https://www.jaipurliving.com/media/wysiwyg/2A5A3712-Weavers_1920x600_1.jpg',
        'cta_primary_text': 'Explore The Artisan Collection',
        'cta_primary_url': '/rugs/',
        'meta_title': 'The Jaipur Living Story & Craft | Artisan Heritage',
        'meta_description': 'Learn about our 40,000 artisans across Rajasthan, India and our purpose-driven heritage since 1978.',
    },
    {
        'page_key': 'trade',
        'page_name': 'Trade Program & Interior Designers',
        'eyebrow': 'EXCLUSIVE FOR THE DESIGN TRADE',
        'title': 'Partner With Jaipur Living',
        'subtitle': 'Exclusive pricing, complimentary swatches, custom sizes and colors, and a dedicated 1:1 account manager to bring your vision to life.',
        'hero_image': 'https://www.jaipurliving.com/media/wysiwyg/SAG_swatches_CYC_RCT_2__26_1_1__1.jpg',
        'section_heading': 'Trade Program Privileges',
        'section_subheading': 'Tailored Benefits for Licensed Professionals',
        'body': 'Designer-Only Margins: Preferred net trade pricing across all rug & decor categories.\nComplimentary Swatches: Free memo samples shipped directly to your studio or client.\nDedicated Concierge: Single point of contact for inventory inquiries, holds, and order logistics.\nCustom Sizing & Shapes: Tailored room dimensions, runners, and custom rug designs.\nNo Minimum Order Value: Full flexibility for boutique residential or large-scale estates.',
        'secondary_image': 'https://www.jaipurliving.com/media/wysiwyg/SAG_swatches_CYC_RCT_2__26_1_1__1.jpg',
        'cta_primary_text': 'Apply For Trade Membership',
        'cta_primary_url': '#tradePortalForm',
        'meta_title': 'Trade Program | Jaipur Living Interior Design Partnership',
        'meta_description': 'Join the Jaipur Living Trade Program for exclusive designer margins, complimentary memo swatches, and custom sizing.',
    },
    {
        'page_key': 'contract',
        'page_name': 'Contract & Commercial Hospitality',
        'eyebrow': 'COMMERCIAL & HOSPITALITY SPECIFICATIONS',
        'title': 'Jaipur Living Contract',
        'subtitle': 'Engineered for demanding hospitality environments, boutique resorts, and commercial developments without compromising bespoke artisan beauty.',
        'hero_image': 'https://www.jaipurliving.com/media/wysiwyg/d08557a2-caf5-420e-95d8-8a828744e85c_2.png',
        'section_heading': 'Engineered For Heavy Foot Traffic',
        'section_subheading': 'Axminster, Hand-Tufted & Solution-Dyed Performance',
        'body': 'Our contract collections combine high-tensile wool blends, solution-dyed performance fibers, and rigorous flammability rating compliance (Class 1 radiant panel testing).\n\n• Custom tufted and axminster weaves\n• Bespoke strike-offs in 10 business days\n• Comprehensive stain-resistant protective coatings\n• Sustainable recycled fiber options',
        'secondary_image': 'https://www.jaipurliving.com/media/wysiwyg/d08557a2-caf5-420e-95d8-8a828744e85c_2.png',
        'cta_primary_text': 'Consult With Contract Team',
        'cta_primary_url': '/become-a-partner/',
        'meta_title': 'Contract & Hospitality Rugs | Jaipur Living',
        'meta_description': 'Custom contract carpets and high-traffic hospitality rugs tailored for luxury hotels, commercial spaces, and resorts.',
    },
    {
        'page_key': 'callaluxe',
        'page_name': 'CallaLuxe Luxury Performance',
        'eyebrow': 'EXCLUSIVE FIBER TECHNOLOGY',
        'title': 'CallaLuxe',
        'subtitle': 'Redefining the new standard in luxury performance rugs. Innovative yarn construction delivers the tactile softness and organic texture of wool with uncompromised resilience against spills, sunlight, and heavy traffic.',
        'hero_image': 'https://www.jaipurliving.com/media/wysiwyg/LS_Grid_Graphic_Website_1_.png',
        'hero_video_url': 'https://player.vimeo.com/video/1226077355?background=1&autoplay=1&loop=1&muted=1',
        'section_heading': 'Innovation & Performance',
        'section_subheading': 'Built for Real Life Moments',
        'body': 'Warp and weft interlock without knots or pile, creating a low-profile flatweave built for the rooms that get used hardest. Color is infused at the fiber\'s core during liquid state so full saturation holds year after year against direct sun and chlorine bleach spot cleaning.',
        'secondary_image': 'https://www.jaipurliving.com/media/wysiwyg/LS_Grid_Graphic_Website_1_.png',
        'cta_primary_text': 'Shop The Collection',
        'cta_primary_url': '#callaluxeCatalog',
        'meta_title': 'CallaLuxe by Jaipur Living | Luxury Performance Rugs',
        'meta_description': 'Explore CallaLuxe bleach-cleanable, ultra-soft luxury performance flatweave rugs engineered exclusively for Jaipur Living.',
    },
    {
        'page_key': 'rugs',
        'page_name': 'Handcrafted Rugs Catalog',
        'eyebrow': 'MASTER WOVEN IN RAJASTHAN',
        'title': 'All Handcrafted Rugs',
        'subtitle': 'Woven knot by knot in Rajasthan, India. Spun from natural wool, luminescent silk, and organic performance yarns.',
        'hero_image': 'https://www.jaipurliving.com/media/wysiwyg/CSN10_RUG168006_RCT_WAV.jpg',
        'section_heading': 'Artisan Quality & Curated Collections',
        'section_subheading': 'Browse by Construction, Size, & Palette',
        'body': 'Browse by collection, knot construction technique, fiber material, dimensions, and color palette. Every rug is backed by authentic generational provenance.',
        'secondary_image': 'https://www.jaipurliving.com/media/wysiwyg/CSN10_RUG168006_RCT_WAV.jpg',
        'cta_primary_text': 'View New Arrivals',
        'cta_primary_url': '/rugs/new.html',
        'meta_title': 'Handcrafted Luxury Rugs | Jaipur Living Catalog',
        'meta_description': 'Explore thousands of hand-knotted, hand-tufted, and flatwoven rugs from Jaipur Living.',
    },
    {
        'page_key': 'decor',
        'page_name': 'Luxury Home Decor & Accessories',
        'eyebrow': 'HANDMADE ACCENTS',
        'title': 'Pillows, Poufs & Accessories',
        'subtitle': 'Handcrafted accents woven by artisans to elevate every corner of the home with tactile richness and harmonious color.',
        'hero_image': 'https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=1200&q=80',
        'section_heading': 'Artisan Accent Collection',
        'section_subheading': 'Woven Pillows & Sculptural Poufs',
        'body': 'Every pillow and pouf is created with natural materials, hand-embroidered details, and durable cotton-linen textures designed to complement our luxury rugs.',
        'secondary_image': 'https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=1200&q=80',
        'cta_primary_text': 'Shop Pillows',
        'cta_primary_url': '/decor/?collection=Pillows',
        'meta_title': 'Luxury Home Decor & Accessories | Jaipur Living',
        'meta_description': 'Elevate your interiors with handcrafted pillows, wool poufs, and luxury decor accents.',
    },
]

for pdata in PAGES_DATA:
    key = pdata['page_key']
    page, created = PageContent.objects.update_or_create(page_key=key, defaults=pdata)
    action = "Created" if created else "Updated"
    print(f"[{action}] Page: {page.page_name} ({key})")

print("All 7 pages content successfully seeded into PageContent database!")
