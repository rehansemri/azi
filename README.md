# Jaipur Living — Luxury Rugs & Home Decor (Django Edition)

A high-fidelity full-stack replica of **[Jaipur Living](https://www.jaipurliving.com)** built using **Python Django**, custom luxury vanilla CSS, and vanilla JavaScript.

---

## 🌟 Key Features

1. **Brand Aesthetics & Design System**:
   - Curated luxury color palette: warm sand (`#f6f5f4`), rich charcoal (`#2b2b2b`), earth clay (`#8c4e41`), and gold accents.
   - Editorial typography using Google Fonts (`Playfair Display`, `Cormorant Garamond`, `Inter`).
   - Sticky navigation with announcement bar and smooth backdrop blur.

2. **Full Mega-Menus**:
   - **Rugs**: Featured collections, color palettes, materials (Wool, Jute, CallaLuxe), construction types (Hand Knotted, Handwoven Flatweave), and size availability.
   - **Decor**: Pillows, poufs, throws, and designer swatches.
   - **Inspiration**: Design edits, artisan stories, and Jaipur Rugs Foundation.
   - **CallaLuxe**: Dedicated luxury performance showcase.

3. **Cinematic Hero Showcase**:
   - Vimeo background video loop (`CallaLuxe Westview`) with gradient scrim and responsive CTAs.

4. **Product Carousel & Canyon Series**:
   - Features real catalog items (`CNL104`, `CNL101`, `CNL102`, `CNL103`) with interactive sizes (`18" Swatch` to `12'X15'`), colorway swatches, dynamic pricing, and "Quick View" modal.

5. **Shoppable Lifestyle Room**:
   - Hotspot button (`View Products`) on the Majnun collection room setting that triggers an interactive slide-up drawer with product items.

6. **Interactive Shopping Bag Drawer**:
   - Slide-out bag with live quantity updates, item removal, dynamic subtotal, and **Free White-Glove Shipping Progress Bar** ($500 threshold).

7. **Project List (Wishlist)**:
   - Interactive heart button toggling products on and off the designer project list with live badge counter updates.

8. **Trade Program Portal**:
   - Dedicated designer application modal and page with multi-field validation and live confirmation.

9. **Django Admin & Database**:
   - SQLite3 database seeded with 18 authentic Jaipur Living products, variants, and categories.
   - Admin panel at `/admin/` (Username: `admin`, Password: `admin123`).

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+
- Django 6+ (`pip install django`)

### 2. Run Server
The server is already running locally on port 8000:
```bash
python manage.py runserver 127.0.0.1:8000
```

Visit the website at: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

### 3. Key Pages
- **Homepage**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **All Rugs Catalog**: [http://127.0.0.1:8000/rugs/](http://127.0.0.1:8000/rugs/)
- **CallaLuxe Innovation**: [http://127.0.0.1:8000/callaluxe/](http://127.0.0.1:8000/callaluxe/)
- **Pillows & Decor**: [http://127.0.0.1:8000/decor/](http://127.0.0.1:8000/decor/)
- **The Jaipur Living Story**: [http://127.0.0.1:8000/the-jaipur-living-story/](http://127.0.0.1:8000/the-jaipur-living-story/)
- **Trade Partner Application**: [http://127.0.0.1:8000/become-a-partner/](http://127.0.0.1:8000/become-a-partner/)
- **Contract & Hospitality**: [http://127.0.0.1:8000/contract/](http://127.0.0.1:8000/contract/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (admin / admin123)
