from PIL import Image, ImageEnhance, ImageFilter
import os

img_path = 'orbit/platform_realistic.jpg'
im = Image.open(img_path)
w, h = im.size

# 1. Soil Strata Cross-Section Texture (Front-Right cutaway)
# Rich humus, roots, embedded sensor chips, clay loam
strata_box = (int(w * 0.45), int(h * 0.45), int(w * 0.92), int(h * 0.78))
tex_strata = im.crop(strata_box)
tex_strata.save('orbit/tex_soil_strata.jpg', quality=95)

# 2. Zone B Cracked Dry Soil Bed Texture
kale_box = (int(w * 0.32), int(h * 0.35), int(w * 0.72), int(h * 0.58))
tex_kale = im.crop(kale_box)
tex_kale.save('orbit/tex_kale_dry_soil.jpg', quality=95)

# 3. Zone A Lush Sweet Corn Canopy Texture
corn_box = (int(w * 0.12), int(h * 0.10), int(w * 0.52), int(h * 0.46))
tex_corn = im.crop(corn_box)
tex_corn.save('orbit/tex_corn_canopy.jpg', quality=95)

# 4. Zone C Soybean Rows Texture
soy_box = (int(w * 0.52), int(h * 0.38), int(w * 0.88), int(h * 0.62))
tex_soy = im.crop(soy_box)
tex_soy.save('orbit/tex_soy_rows.jpg', quality=95)

# 5. Solar Panel / IoT Gateway Crop
solar_box = (int(w * 0.44), int(h * 0.06), int(w * 0.56), int(h * 0.38))
tex_solar = im.crop(solar_box)
tex_solar.save('orbit/tex_solar_mast.jpg', quality=95)

print("Generated PBR textures successfully!")
