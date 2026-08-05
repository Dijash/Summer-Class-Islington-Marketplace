import os
import sys
import urllib.request
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from django.conf import settings
from core.models import HeroBanner, BrandSpotlight, FeaturedCategory, ShopDrop, Category
from product.models import Product, ProductImage, ProductColor

DEFAULT_FALLBACK = 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80'

IMAGE_MAP = {
    # Hero Banners
    'summer_sale': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80',
    'electronics': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80',
    'luxury_designer': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=80',
    
    # Categories / Types
    'kurtas': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
    'dresses': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=800&q=80',
    'formal_men': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80',
    'tops_tees': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80',
    'denim': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80',
    'handbags': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80',
    'sneakers': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80',
    'casual_shirts': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80',
    'ethnic': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80',
    'jackets': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80',
    'watches': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80',
    'footwear': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80',
    'lingerie': 'https://images.unsplash.com/photo-1583846783214-7229a91b20ed?auto=format&fit=crop&w=800&q=80',
    'kidswear': 'https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=800&q=80',
    'eyewear': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=800&q=80',
    'luggage': 'https://images.unsplash.com/photo-1581553680321-4fffae59febd?auto=format&fit=crop&w=800&q=80',
    'activewear': 'https://images.unsplash.com/photo-1518310383802-640c2de311b2?auto=format&fit=crop&w=800&q=80',
    'beauty': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80',
    'jewellery': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80',
    'perfume': 'https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=800&q=80',
    'home_decor': 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80',
    'tech': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80',
    'womenswear': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
    'menswear': 'https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?auto=format&fit=crop&w=800&q=80',
    
    # Brands
    'nike': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80',
    'adidas': 'https://images.unsplash.com/photo-1518002171953-a080ee817e1f?auto=format&fit=crop&w=800&q=80',
    'puma': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=800&q=80',
    'zara': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
    'hm': 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=800&q=80',
    'gucci': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=800&q=80',
    'levis': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80',
    'calvin_klein': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80',
    'tommy': 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?auto=format&fit=crop&w=800&q=80',
    'hugo_boss': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80',
    'ralph_lauren': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80',
    'daali': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
    'libas': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80',
    'rang_manch': 'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=800&q=80',
    'lakme': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80',
    'w_aurelia': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
    'mango': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=800&q=80',
    'vero_moda': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
    'jack_jones': 'https://images.unsplash.com/photo-1516257984-b1b4d707412e?auto=format&fit=crop&w=800&q=80',
    'lacoste': 'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?auto=format&fit=crop&w=800&q=80',
    'diesel': 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=800&q=80',
    'raymond': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80',

    # Specific Product Titles
    'desk_lamp': 'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=800&q=80',
    'running_shoes': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80',
    'coffee_machine': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80',
    'denim_jacket': 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=800&q=80',
    'speaker': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80',
    'keyboard': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80',
    'tv': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80',
    'shirt': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80',
    'office_chair': 'https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&w=800&q=80',
    'fitness_watch': 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=800&q=80',
}

def get_url_for_text(text):
    t = text.lower()
    if 'lamp' in t: return IMAGE_MAP['desk_lamp']
    if 'running' in t or 'sneaker' in t or 'shoe' in t or 'kicks' in t or 'footwear' in t: return IMAGE_MAP['running_shoes']
    if 'coffee' in t or 'barista' in t: return IMAGE_MAP['coffee_machine']
    if 'denim' in t or 'jeans' in t: return IMAGE_MAP['denim_jacket']
    if 'speaker' in t or 'audio' in t: return IMAGE_MAP['speaker']
    if 'keyboard' in t: return IMAGE_MAP['keyboard']
    if 'tv' in t or 'screen' in t: return IMAGE_MAP['tv']
    if 'shirt' in t or 'tee' in t or 'top' in t: return IMAGE_MAP['shirt']
    if 'chair' in t: return IMAGE_MAP['office_chair']
    if 'tracker' in t or 'watch' in t: return IMAGE_MAP['watches']
    if 'kurta' in t or 'suit set' in t or 'ethnic' in t or 'indian' in t: return IMAGE_MAP['kurtas']
    if 'dress' in t or 'women' in t: return IMAGE_MAP['dresses']
    if 'formal' in t or 'menswear' in t: return IMAGE_MAP['formal_men']
    if 'handbag' in t or 'bag' in t: return IMAGE_MAP['handbags']
    if 'jacket' in t or 'coat' in t: return IMAGE_MAP['jackets']
    if 'lingerie' in t or 'under' in t: return IMAGE_MAP['lingerie']
    if 'kid' in t: return IMAGE_MAP['kidswear']
    if 'eyewear' in t or 'sunglass' in t or 'shade' in t: return IMAGE_MAP['eyewear']
    if 'luggage' in t: return IMAGE_MAP['luggage']
    if 'activewear' in t or 'gym' in t or 'sport' in t: return IMAGE_MAP['activewear']
    if 'beauty' in t or 'makeup' in t or 'cosmetic' in t: return IMAGE_MAP['beauty']
    if 'jewel' in t or 'ring' in t: return IMAGE_MAP['jewellery']
    if 'perfume' in t or 'fragrance' in t: return IMAGE_MAP['perfume']
    if 'home' in t or 'decor' in t: return IMAGE_MAP['home_decor']
    if 'tech' in t or 'gadget' in t: return IMAGE_MAP['tech']
    if 'nike' in t: return IMAGE_MAP['nike']
    if 'adidas' in t: return IMAGE_MAP['adidas']
    if 'puma' in t: return IMAGE_MAP['puma']
    if 'zara' in t: return IMAGE_MAP['zara']
    if 'h&m' in t: return IMAGE_MAP['hm']
    if 'gucci' in t: return IMAGE_MAP['gucci']
    if 'levi' in t: return IMAGE_MAP['levis']
    if 'calvin' in t: return IMAGE_MAP['calvin_klein']
    if 'tommy' in t: return IMAGE_MAP['tommy']
    if 'hugo' in t: return IMAGE_MAP['hugo_boss']
    if 'ralph' in t: return IMAGE_MAP['ralph_lauren']
    if 'daali' in t: return IMAGE_MAP['daali']
    if 'libas' in t: return IMAGE_MAP['libas']
    if 'rang' in t: return IMAGE_MAP['rang_manch']
    if 'lakme' in t or 'maybelline' in t: return IMAGE_MAP['lakme']
    if 'aurelia' in t or 'w &' in t: return IMAGE_MAP['w_aurelia']
    if 'mango' in t: return IMAGE_MAP['mango']
    if 'vero' in t: return IMAGE_MAP['vero_moda']
    if 'jack' in t: return IMAGE_MAP['jack_jones']
    if 'lacoste' in t: return IMAGE_MAP['lacoste']
    if 'diesel' in t: return IMAGE_MAP['diesel']
    if 'raymond' in t: return IMAGE_MAP['raymond']
    return IMAGE_MAP['womenswear']

def sanitize(name):
    return name.lower().replace("'", "").replace(" ", "-").replace("&", "and")

def download_and_save(url, rel_path):
    full_media_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    full_static_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', rel_path)
    
    os.makedirs(os.path.dirname(full_media_path), exist_ok=True)
    os.makedirs(os.path.dirname(full_static_path), exist_ok=True)
    
    if not os.path.exists(full_media_path) or os.path.getsize(full_media_path) < 1000:
        print(f"Downloading {rel_path}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp, open(full_media_path, 'wb') as out_f:
                data = resp.read()
                out_f.write(data)
                with open(full_static_path, 'wb') as static_out_f:
                    static_out_f.write(data)
        except Exception as e:
            print(f"Error downloading {url}: {e}. Retrying fallback...")
            try:
                req_fallback = urllib.request.Request(DEFAULT_FALLBACK, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_fallback) as resp, open(full_media_path, 'wb') as out_f:
                    data = resp.read()
                    out_f.write(data)
                    with open(full_static_path, 'wb') as static_out_f:
                        static_out_f.write(data)
            except Exception as e2:
                print(f"Fallback download error: {e2}")
                return None
    else:
        if not os.path.exists(full_static_path):
            with open(full_media_path, 'rb') as f_in, open(full_static_path, 'wb') as f_out:
                f_out.write(f_in.read())
    return rel_path

def main():
    print("=== STARTING IMAGE UPDATE PROCESS ===")

    # 1. Hero Banners
    print("\nProcessing Hero Banners...")
    for hb in HeroBanner.objects.all():
        url = get_url_for_text(hb.title + " " + hb.subtitle)
        filename = f"hero_{hb.id}.jpg"
        rel_path = os.path.join('hero_banners', filename)
        if download_and_save(url, rel_path):
            hb.image = rel_path
            hb.image_url = f"/media/{rel_path}"
            hb.save()

    # 2. Brand Spotlights
    print("\nProcessing Brand Spotlights...")
    for bs in BrandSpotlight.objects.all():
        url = get_url_for_text(f"{bs.name} {bs.category} {bs.discount_tag}")
        filename = f"{bs.category}_{sanitize(bs.name)}.jpg"
        rel_path = os.path.join('brand_spotlights', filename)
        if download_and_save(url, rel_path):
            bs.image = rel_path
            bs.image_url = f"/media/{rel_path}"
            bs.save()

    # 3. Featured Categories
    print("\nProcessing Featured Categories...")
    for fc in FeaturedCategory.objects.all():
        if fc.is_promo_card:
            continue
        url = get_url_for_text(fc.title + " " + fc.brand_sub_title)
        filename = f"cat_{sanitize(fc.title)}.jpg"
        rel_path = os.path.join('featured_categories', filename)
        if download_and_save(url, rel_path):
            fc.image = rel_path
            fc.image_url = f"/media/{rel_path}"
            fc.save()

    # 4. Shop Drops
    print("\nProcessing Shop Drops...")
    for sd in ShopDrop.objects.all():
        if sd.is_promo_card:
            continue
        url = get_url_for_text(sd.title + " " + sd.offer_tag)
        filename = f"drop_{sanitize(sd.title)}.jpg"
        rel_path = os.path.join('shop_drop', filename)
        if download_and_save(url, rel_path):
            sd.image = rel_path
            sd.image_url = f"/media/{rel_path}"
            sd.save()

    # 5. Categories
    print("\nProcessing Categories...")
    for cat in Category.objects.all():
        url = get_url_for_text(cat.name)
        filename = f"cat_{cat.slug}.jpg"
        rel_path = os.path.join('categories', filename)
        if download_and_save(url, rel_path):
            cat.image = rel_path
            cat.save()

    # 6. Products & Product Images
    print("\nProcessing Products & Product Images...")
    for p in Product.objects.all():
        url = get_url_for_text(f"{p.brand_name} {p.title} {p.category.name}")
        filename = f"product_{p.id}_{sanitize(p.slug[:30])}.jpg"
        rel_path = os.path.join('products', filename)
        if download_and_save(url, rel_path):
            media_url = f"/media/{rel_path}"
            colors = p.colors.all()
            if not colors.exists():
                col = ProductColor.objects.create(
                    product=p,
                    color_name='Default',
                    color_code='#000000',
                    swatch_image_url=media_url,
                    is_default=True
                )
                ProductImage.objects.create(
                    color_variant=col,
                    image_url=media_url,
                    angle_label='Front View',
                    order=0
                )
            else:
                for col in colors:
                    if not col.swatch_image_url:
                        col.swatch_image_url = media_url
                        col.save()
                    if not col.images.exists():
                        ProductImage.objects.create(
                            color_variant=col,
                            image_url=media_url,
                            angle_label='Front View',
                            order=0
                        )
                    else:
                        for img in col.images.all():
                            img.image_url = media_url
                            img.save()

    print("\n=== FINISHED ALL IMAGE UPDATES SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
