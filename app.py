from itertools import permutations
from math import radians, sin, cos, sqrt, atan2
from itertools import permutations
import requests
import time

# Fonction pour calculer la distance entre deux points GPS (Haversine)
def distance(lat1, lon1, lat2, lon2):
    R = 6371  # rayon de la Terre en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Fonction pour géocoder une adresse en latitude/longitude via Nominatim
def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "IDEL-Optimiseur/1.0"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return lat, lon
    else:
        print(f"Adresse non trouvée : {address}")
        return None, None

# Liste des patients : (nom, adresse, durée_soin_en_min)
patients = [
    ("Patient A", "48 Rue de Rivoli, Paris", 30),
    ("Patient B", "Champ de Mars, 5 Avenue Anatole France, Paris", 20),
    ("Patient C", "Champs-Élysées, Paris", 40),
    ("Patient D", "Notre-Dame, Paris", 25)
]

# Adresse du point de départ (cabinet IDEL)
start_address = "Louvre, Paris"

# Géocodage du point de départ
start_lat, start_lon = geocode_address(start_address)
if start_lat is None or start_lon is None:
    print("Erreur : Impossible de géocoder l'adresse de départ")
    exit(1)

# Géocodage des patients
patients_geocoded = []
for nom, adresse, duree in patients:
    lat, lon = geocode_address(adresse)
    if lat is None or lon is None:
        print(f"Attention : Impossible de géocoder l'adresse de {nom}, elle sera ignorée")
        continue
    patients_geocoded.append((nom, lat, lon, duree))
    time.sleep(1)  # pause pour éviter de surcharger le service

# Fonction pour trouver la tournée optimale
def tournée_optimale(patients, start):
    best_order = None
    best_distance = float('inf')
    n = len(patients)

    for perm in permutations(patients):
        dist = 0
        dist += distance(start[0], start[1], perm[0][1], perm[0][2])
        for i in range(n - 1):
            dist += distance(perm[i][1], perm[i][2], perm[i + 1][1], perm[i + 1][2])
        # Optionnel : retour au départ
        # dist += distance(perm[-1][1], perm[-1][2], start[0], start[1])

        if dist < best_distance:
            best_distance = dist
            best_order = perm

    return best_order, best_distance

# Calcul de la tournée optimale
ordre_opt, dist_totale = tournée_optimale(patients_geocoded, (start_lat, start_lon))

# Calcul du temps total (soins + trajets)
temps_soins = sum(p[3] for p in ordre_opt)
vitesse_moyenne = 25  # km/h en zone urbaine, ajustable
temps_trajet = (dist_totale / vitesse_moyenne) * 60  # en minutes
temps_total = temps_soins + temps_trajet

# Affichage
print("Ordre optimisé des visites :")
for i, p in enumerate(ordre_opt, 1):
    print(f"{i}. {p[0]} - Durée soin: {p[3]} min")

print(f"\nDistance totale estimée : {dist_totale:.2f} km")
print(f"Temps total estimé (soins + trajets) : {temps_total:.0f} minutes")
