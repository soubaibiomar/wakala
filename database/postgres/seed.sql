-- seed.sql
-- Create a test user
INSERT INTO users (id, full_name, email, phone, hashed_password, role, is_verified, is_pro)
VALUES (
    '11111111-1111-1111-1111-111111111111', 
    'Test Seller', 
    'test@wakala.ma', 
    '+212600000000',
    'hashed', 
    'seller', 
    true, 
    false
) ON CONFLICT (email) DO NOTHING;

-- Create Vehicle 1
INSERT INTO vehicles (id, seller_id, brand, model, version, year, mileage, fuel_type, body_type, transmission, city, price, condition_score, popularity_score, description)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    'Peugeot',
    '208',
    'Active',
    2021,
    45000,
    'diesel',
    'citadine',
    'manuelle',
    'Casablanca',
    145000.0,
    85,
    0.9,
    'Voiture première main, entretien régulier. Idéale pour la ville.'
) ON CONFLICT (id) DO NOTHING;

-- Create Listing 1
INSERT INTO listings (id, vehicle_id, status, published_at, images_urls)
VALUES (
    '33333333-3333-3333-3333-333333333333',
    '22222222-2222-2222-2222-222222222222',
    'active',
    NOW(),
    '{"https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600"}'
) ON CONFLICT (id) DO NOTHING;

-- Create Vehicle 2
INSERT INTO vehicles (id, seller_id, brand, model, version, year, mileage, fuel_type, body_type, transmission, city, price, condition_score, popularity_score, description)
VALUES (
    '44444444-4444-4444-4444-444444444444',
    '11111111-1111-1111-1111-111111111111',
    'Volkswagen',
    'Golf 8',
    'R-Line',
    2022,
    15000,
    'diesel',
    'berline',
    'automatique',
    'Rabat',
    320000.0,
    95,
    0.95,
    'Toutes options, état neuf.'
) ON CONFLICT (id) DO NOTHING;

-- Create Listing 2
INSERT INTO listings (id, vehicle_id, status, published_at, images_urls)
VALUES (
    '55555555-5555-5555-5555-555555555555',
    '44444444-4444-4444-4444-444444444444',
    'active',
    NOW(),
    '{"https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=600"}'
) ON CONFLICT (id) DO NOTHING;

-- Create Vehicle 3
INSERT INTO vehicles (id, seller_id, brand, model, version, year, mileage, fuel_type, body_type, transmission, city, price, condition_score, popularity_score, description)
VALUES (
    '66666666-6666-6666-6666-666666666666',
    '11111111-1111-1111-1111-111111111111',
    'Dacia',
    'Duster',
    'Prestige',
    2020,
    80000,
    'diesel',
    'suv',
    'manuelle',
    'Marrakech',
    125000.0,
    70,
    0.8,
    'Bon état, robuste pour tous les chemins.'
) ON CONFLICT (id) DO NOTHING;

-- Create Listing 3
INSERT INTO listings (id, vehicle_id, status, published_at, images_urls)
VALUES (
    '77777777-7777-7777-7777-777777777777',
    '66666666-6666-6666-6666-666666666666',
    'active',
    NOW(),
    '{"https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=600"}'
) ON CONFLICT (id) DO NOTHING;
