"""
outreach/message_templates.py — Templates de messages pour les 6 jalons
de la séquence d'outreach 0-60 jours.

Les variables sont injectées depuis les données réelles du moteur B
(nom, véhicule, chiffres réels) — JAMAIS de valeur inventée dans un template.

Ton non intrusif, informatif, jamais culpabilisant, toujours une porte
de sortie claire.
"""

from typing import Any, Optional


def _format_price(price: float) -> str:
    """Formate un prix en MAD lisible."""
    return f"{price:,.0f} MAD".replace(",", " ")


def _format_vehicle_name(vehicle: dict) -> str:
    """Formate le nom complet d'un véhicule."""
    brand = vehicle.get("brand", "")
    model = vehicle.get("model", "")
    version = vehicle.get("version", "")
    year = vehicle.get("year", "")
    name = f"{brand} {model}"
    if version:
        name += f" {version}"
    if year:
        name += f" ({year})"
    return name.strip()


# ══════════════════════════════════════════════════════════════════
# Templates par jalon
# ══════════════════════════════════════════════════════════════════

TEMPLATES: dict[str, dict[str, str]] = {
    # ── J0 : Récapitulatif Top 3 ─────────────────────────────────
    "j0_recap_top3": {
        "subject": "Votre sélection personnalisée Wakala — {top1_name}",
        "body": """Bonjour {prospect_name},

Merci pour notre échange ! Voici votre sélection personnalisée basée sur vos critères :

🥇 **{top1_name}** — {top1_price}
   Points forts : {top1_strengths}
   {top1_compromises}

🥈 **{top2_name}** — {top2_price}
   Points forts : {top2_strengths}
   {top2_compromises}

🥉 **{top3_name}** — {top3_price}
   Points forts : {top3_strengths}
   {top3_compromises}

Ces recommandations sont basées sur votre budget de {budget} et votre usage {usage}.

Bonne réflexion,
L'équipe Wakala

---
_Vous pouvez vous désabonner à tout moment en répondant STOP._""",
    },

    # ── J2-3 : Catalogue interactif ──────────────────────────────
    "j2_catalogue_interactif": {
        "subject": "📋 Fiches détaillées de vos véhicules sélectionnés",
        "body": """Bonjour {prospect_name},

Pour vous aider dans votre réflexion, voici les fiches détaillées de votre Top 3 :

• {top1_name} — Fiche complète : consommation {top1_consumption}, {top1_fuel_type}
• {top2_name} — Fiche complète : consommation {top2_consumption}, {top2_fuel_type}
• {top3_name} — Fiche complète : consommation {top3_consumption}, {top3_fuel_type}

N'hésitez pas à me poser toute question sur ces modèles.

Wakala

_Répondez STOP pour ne plus recevoir de messages._""",
    },

    # ── J7 : Matrice TCO ─────────────────────────────────────────
    "j7_matrice_tco": {
        "subject": "💰 Comparatif coût total — Quel véhicule vous coûtera le moins ?",
        "body": """Bonjour {prospect_name},

Au-delà du prix d'achat, voici une estimation du coût total de possession sur 5 ans :

| Véhicule | Prix | Conso. estimée/an | Score Coût réel |
|----------|------|-------------------|-----------------|
| {top1_name} | {top1_price} | {top1_annual_fuel} | {top1_cost_score}/5 |
| {top2_name} | {top2_price} | {top2_annual_fuel} | {top2_cost_score}/5 |
| {top3_name} | {top3_price} | {top3_annual_fuel} | {top3_cost_score}/5 |

_Ces estimations sont basées sur les données techniques des constructeurs et le prix moyen du carburant au Maroc._

Wakala

_Répondez STOP pour ne plus recevoir de messages._""",
    },

    # ── J14 : Essai routier ──────────────────────────────────────
    "j14_essai_routier": {
        "subject": "🚗 Envie de tester votre favori ?",
        "body": """Bonjour {prospect_name},

Après réflexion, si un des modèles suivants vous intéresse particulièrement, nous pouvons vous mettre en relation avec un concessionnaire près de chez vous pour un essai :

• {top1_name}
• {top2_name}
• {top3_name}

Répondez simplement avec le modèle qui vous intéresse, ou ignorez ce message — aucune obligation.

Wakala

_Répondez STOP pour ne plus recevoir de messages._""",
    },

    # ── J45 : Alerte prix (UNIQUEMENT si baisse réelle détectée) ──
    "j45_alerte_prix": {
        "subject": "📉 Bonne nouvelle — Baisse de prix détectée",
        "body": """Bonjour {prospect_name},

Nous avons détecté une baisse de prix sur un véhicule de votre sélection :

**{vehicle_name}**
• Ancien prix : {old_price}
• Nouveau prix : {new_price}
• Économie : {savings}

Cette baisse est basée sur les prix actuels des concessionnaires.

Wakala

_Répondez STOP pour ne plus recevoir de messages._""",
    },

    # ── J60 : Clôture bienveillante ──────────────────────────────
    "j60_cloture": {
        "subject": "🙏 Fin de votre suivi personnalisé Wakala",
        "body": """Bonjour {prospect_name},

Cela fait maintenant 60 jours que nous vous accompagnons dans votre recherche automobile.

Ce message est le dernier de notre suivi automatique. Votre dossier de recommandation reste disponible si vous souhaitez le consulter à nouveau.

Si vous avez trouvé votre véhicule, félicitations ! 🎉
Sinon, n'hésitez pas à relancer une nouvelle recherche quand vous le souhaitez.

Merci de votre confiance,
L'équipe Wakala""",
    },
}


def render_template(
    template_key: str,
    variables: dict[str, Any],
) -> dict[str, str]:
    """
    Rend un template avec les variables fournies.
    Retourne {'subject': ..., 'body': ...}.

    Si une variable est manquante, la laisse comme placeholder
    plutôt que de crasher — mais logge un warning.
    """
    template = TEMPLATES.get(template_key)
    if not template:
        return {
            "subject": f"[Wakala] Message — {template_key}",
            "body": f"Template '{template_key}' non trouvé.",
        }

    import logging
    logger = logging.getLogger(__name__)

    try:
        subject = template["subject"].format(**variables)
    except KeyError as e:
        logger.warning("Template %s: missing variable %s in subject", template_key, e)
        subject = template["subject"]

    try:
        body = template["body"].format(**variables)
    except KeyError as e:
        logger.warning("Template %s: missing variable %s in body", template_key, e)
        body = template["body"]

    return {"subject": subject, "body": body}


def build_top3_variables(
    prospect_name: str,
    vehicles: list[dict],
    budget: Optional[float] = None,
    usage: Optional[str] = None,
) -> dict[str, Any]:
    """
    Construit les variables pour les templates Top 3 à partir des
    données réelles du moteur B.
    """
    variables: dict[str, Any] = {
        "prospect_name": prospect_name,
        "budget": _format_price(budget) if budget else "non précisé",
        "usage": usage or "général",
    }

    for i, v in enumerate(vehicles[:3], 1):
        prefix = f"top{i}"
        variables[f"{prefix}_name"] = _format_vehicle_name(v)
        variables[f"{prefix}_price"] = _format_price(v.get("price", 0))

        strengths = v.get("strengths", [])
        variables[f"{prefix}_strengths"] = ", ".join(strengths) if strengths else "Équilibré"

        compromises = v.get("compromises", [])
        if compromises:
            variables[f"{prefix}_compromises"] = "⚠ Compromis : " + ", ".join(compromises)
        else:
            variables[f"{prefix}_compromises"] = ""

        variables[f"{prefix}_consumption"] = f"{v.get('fuel_consumption', 'N/A')} L/100km"
        variables[f"{prefix}_fuel_type"] = v.get("fuel_type", "N/A")
        variables[f"{prefix}_annual_fuel"] = f"~{int(v.get('fuel_consumption', 6) * 15000 / 100 * 12)} MAD"
        variables[f"{prefix}_cost_score"] = v.get("scores", {}).get("cout_reel", "N/A")

    return variables
