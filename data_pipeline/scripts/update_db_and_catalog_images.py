import json
import re

# 1. Load scraped images & curated images
with open('data_pipeline/scripts/scraped_moteur_images.json', 'r', encoding='utf-8') as f:
    scraped = json.load(f)

with open('data_pipeline/scripts/curated_studio_images.json', 'r', encoding='utf-8') as f:
    curated = json.load(f)

# Build comprehensive studio dictionary
studio_dict = {}

# Ingest scraped images
for brand_name, models_dict in scraped.items():
    b_clean = brand_name.lower().strip()
    if b_clean not in studio_dict:
        studio_dict[b_clean] = {}
    for mod_name, img_url in models_dict.items():
        if img_url and img_url.startswith('http') and ('storage/media/images/models/' in img_url or 'group.renault.com' in img_url or 'files/' in img_url or 'Voiture-Neuve/' in img_url):
            m_clean = mod_name.lower().replace(b_clean, '').strip()
            m_clean = re.sub(r'à partir de.*', '', m_clean)
            m_clean = re.sub(r'\d+\s*versions.*', '', m_clean)
            m_clean = m_clean.strip()
            if m_clean:
                studio_dict[b_clean][m_clean] = img_url
            studio_dict[b_clean][mod_name.lower().strip()] = img_url

# Ingest curated images (overriding any generic ones)
for key, img_url in curated.items():
    brand_name, mod_name = key.split('|', 1)
    b_clean = brand_name.lower().strip()
    m_clean = mod_name.lower().strip()
    if b_clean not in studio_dict:
        studio_dict[b_clean] = {}
    studio_dict[b_clean][m_clean] = img_url
    clean_no_brand = m_clean.replace(b_clean, '').strip()
    if clean_no_brand:
        studio_dict[b_clean][clean_no_brand] = img_url

# Ensure Dacia explicit models
studio_dict['dacia'] = {
    'bigster': 'https://www.moteur.ma/storage/media/images/models/nouvelle-bigster-327.png',
    'dacia bigster': 'https://www.moteur.ma/storage/media/images/models/nouvelle-bigster-327.png',
    'duster': 'https://www.moteur.ma/storage/media/images/models/nouvelle-duster-332.png',
    'dacia duster': 'https://www.moteur.ma/storage/media/images/models/nouvelle-duster-332.png',
    'duster 3': 'https://www.moteur.ma/storage/media/images/models/nouvelle-duster-332.png',
    'jogger': 'https://www.moteur.ma/storage/media/images/models/nouvelle-jogger-873.jpg',
    'dacia jogger': 'https://www.moteur.ma/storage/media/images/models/nouvelle-jogger-873.jpg',
    'logan': 'https://www.moteur.ma/storage/media/images/models/nouvelle-logan-200.png',
    'dacia logan': 'https://www.moteur.ma/storage/media/images/models/nouvelle-logan-200.png',
    'sandero': 'https://www.moteur.ma/storage/media/images/models/nouvelle-sandero-947.png',
    'dacia sandero': 'https://www.moteur.ma/storage/media/images/models/nouvelle-sandero-947.png',
    'sandero stepway': 'https://cdn.group.renault.com/dac/fr/vehicules/sandero/sandero-stepway-bji-ph1/decouverte/dacia-sandero-stepway-bji-ph1-001.jpg',
    'sandero-stepway': 'https://cdn.group.renault.com/dac/fr/vehicules/sandero/sandero-stepway-bji-ph1/decouverte/dacia-sandero-stepway-bji-ph1-001.jpg',
    'dacia sandero-stepway': 'https://cdn.group.renault.com/dac/fr/vehicules/sandero/sandero-stepway-bji-ph1/decouverte/dacia-sandero-stepway-bji-ph1-001.jpg',
    'sandero streetway': 'https://www.moteur.ma/storage/media/images/models/nouvelle-sandero-947.png',
    'dacia sandero streetway': 'https://www.moteur.ma/storage/media/images/models/nouvelle-sandero-947.png',
    'spring': 'https://www.moteur.ma/storage/media/images/models/nouvelle-spring-259.png',
    'dacia spring': 'https://www.moteur.ma/storage/media/images/models/nouvelle-spring-259.png',
}

# Write frontend/src/utils/vehicleImageCatalogData.ts
ts_content = "export const VEHICLE_STUDIO_IMAGES: Record<string, Record<string, string>> = " + json.dumps(studio_dict, ensure_ascii=False, indent=2) + ";\n\n" + """export const BODY_FALLBACKS = {
  suv: 'https://www.moteur.ma/storage/media/images/models/nouvelle-duster-332.png',
  citadine: 'https://www.moteur.ma/storage/media/images/models/nouvelle-sandero-947.png',
  berline: 'https://www.moteur.ma/storage/media/images/models/nouvelle-logan-200.png',
  default: 'https://www.moteur.ma/storage/media/images/models/nouvelle-duster-332.png',
};
"""

with open('frontend/src/utils/vehicleImageCatalogData.ts', 'w', encoding='utf-8') as f:
    f.write(ts_content)

print('Updated frontend/src/utils/vehicleImageCatalogData.ts with all curated and scraped studio cutouts!')
