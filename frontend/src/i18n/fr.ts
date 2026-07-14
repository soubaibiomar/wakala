const fr = {
  // ─── Navigation ────────────────────────────────────
  nav: {
    home: "Accueil",
    catalogue: "Catalogue",
    dashboard: "Tableau de bord",
    login: "Connexion",
    register: "Inscription",
    logout: "Déconnexion",
  },

  // ─── Hero ──────────────────────────────────────────
  hero: {
    title: "Trouvez la voiture de vos rêves au Maroc",
    subtitle: "Intelligence artificielle au service de votre achat automobile",
    searchPlaceholder: "Marque, modèle, ville…",
    cta: "Explorer le catalogue",
  },

  // ─── Catalogue / Filtres ───────────────────────────
  catalogue: {
    title: "Catalogue véhicules",
    emptyTitle: "Aucun résultat",
    emptyDescription: "Essayez de modifier vos filtres ou d'élargir votre recherche.",
    sortBy: "Trier par",
    sortPriceAsc: "Prix croissant",
    sortPriceDesc: "Prix décroissant",
    sortYear: "Année",
    sortMileage: "Kilométrage",
    sortRelevance: "Pertinence",
  },

  // ─── Filtres ───────────────────────────────────────
  filters: {
    budget: "Budget (MAD)",
    city: "Ville",
    cityPlaceholder: "Ex : Casablanca",
    brand: "Marque",
    model: "Modèle",
    year: "Année",
    fuel: "Carburant",
    bodyType: "Type de carrosserie",
    mileage: "Kilométrage max",
    search: "Rechercher",
    reset: "Réinitialiser",
    saveSearch: "Enregistrer la recherche",
  },

  // ─── Véhicule ──────────────────────────────────────
  vehicle: {
    price: "Prix",
    mad: "MAD",
    mileage: "Kilométrage",
    year: "Année",
    fuel: "Carburant",
    transmission: "Transmission",
    bodyType: "Type",
    color: "Couleur",
    doors: "Portes",
    seats: "Places",
    engine: "Moteur",
    power: "Puissance",
    status: "Statut",
    active: "Actif",
    sold: "Vendu",
    contact: "Contacter le vendeur",
    estimatedPrice: "Prix marché estimé",
    trustScore: "Score de confiance",
    noImage: "Image non disponible",
    plateBlurred: "Plaque floutée (conformité CNDP)",
    city: "Ville",
  },

  // ─── Chatbot ───────────────────────────────────────
  chatbot: {
    title: "Wakala Assistant",
    placeholder: "Posez votre question…",
    suggestion1: "SUV essence entre 200 000 et 300 000 MAD",
    suggestion2: "Citadine économique à Casablanca",
    suggestion3: "Quels sont les véhicules les plus fiables ?",
    errorMessage: "Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer.",
    typing: "réfléchit…",
    source: "Source",
  },

  // ─── Auth ──────────────────────────────────────────
  auth: {
    loginTitle: "Connexion",
    registerTitle: "Créer un compte",
    email: "Adresse email",
    password: "Mot de passe",
    name: "Nom complet",
    phone: "Téléphone",
    cin: "CIN",
    phonePlaceholder: "+212612345678",
    cinPlaceholder: "AB123456",
    submitLogin: "Se connecter",
    submitRegister: "Créer mon compte",
    noAccount: "Pas encore de compte ?",
    haveAccount: "Déjà un compte ?",
    loginLink: "Connectez-vous",
    registerLink: "Inscrivez-vous",
    passwordRules: "8 caractères min, 1 majuscule, 1 chiffre",
    phoneError: "Format attendu : +2126XXXXXXXX",
    cinError: "Format attendu : AB123456",
    loginError: "Email ou mot de passe incorrect",
    roleBuyer: "Acheteur",
    roleSeller: "Vendeur",
  },

  // ─── Vendeur Dashboard ────────────────────────────
  dashboard: {
    title: "Tableau de bord vendeur",
    totalViews: "Vues totales",
    avgTrustScore: "Score confiance moyen",
    priceComparison: "Prix suggéré vs affiché",
    myListings: "Mes annonces",
    createListing: "Créer une annonce",
    estimatePrice: "Estimer le prix",
    statusActive: "Actif",
    statusSold: "Vendu",
    statusFlagged: "Signalé",
    activeListings: "Annonces actives",
    soldListings: "Vendues",
    pendingListings: "En attente",
    noListings: "Vous n'avez pas encore d'annonces.",
  },

  // ─── Trust Score ──────────────────────────────────
  trust: {
    title: "Atelier / Confiance",
    verifiedSeller: "Vendeur vérifié",
    documentedMaintenance: "Entretien documenté",
    availableHistory: "Historique disponible",
    plateBlurred: "Plaque floutée",
    cndpCompliant: "Conforme CNDP",
  },

  // ─── Erreurs / Messages ───────────────────────────
  error: {
    generic: "Une erreur est survenue. Veuillez réessayer.",
    notFound: "Page introuvable",
    forbidden: "Accès refusé",
    networkError: "Erreur réseau — vérifiez votre connexion.",
    sessionExpired: "Session expirée — veuillez vous reconnecter.",
  },

  // ─── Général ──────────────────────────────────────
  general: {
    loading: "Chargement…",
    save: "Enregistrer",
    cancel: "Annuler",
    delete: "Supprimer",
    confirm: "Confirmer",
    back: "Retour",
    next: "Suivant",
    previous: "Précédent",
    close: "Fermer",
    currency: "MAD",
  },
};

export default fr;
export type Translations = typeof fr;
