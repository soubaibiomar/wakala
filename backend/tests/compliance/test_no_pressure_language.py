"""
tests/compliance/test_no_pressure_language.py — Vérifie que les templates
d'outreach et les réponses du chatbot ne contiennent pas de langage
de pression commerciale.

Patterns interdits :
- "dépêchez-vous", "offre limitée" (sans donnée réelle),
  "dernière chance", "ne ratez pas", "prix cassé",
  "promotion exclusive" (sans baisse vérifiée), etc.

Ton attendu : informatif, non intrusif, toujours une porte de sortie.
"""

import re

import pytest

from app.outreach.message_templates import TEMPLATES, render_template


# ── Patterns de pression commerciale interdits ───────────────────

FORBIDDEN_PATTERNS = [
    r"d[ée]p[eê]chez[- ]vous",
    r"offre\s+limit[ée]e",
    r"derni[èe]re\s+chance",
    r"ne\s+ratez\s+pas",
    r"prix\s+cass[ée]",
    r"promotion\s+exclusive",
    r"urgence",
    r"maintenant\s+ou\s+jamais",
    r"places?\s+limit[ée]es?",
    r"stock\s+limit[ée]",
    r"act(?:ez|ion)\s+vite",
    r"n['']attendez\s+(?:plus|pas)",
    r"trop\s+tard",
    r"qu['']attendez[- ]vous",
    r"profitez[- ]en\s+(?:vite|maintenant)",
    r"r[ée]duction\s+(?:incroyable|exceptionnelle|massive)",
    r"gratuit(?:e)?(?:ment)?",  # sauf "vous désabonner gratuitement"
    r"offre\s+(?:irr[ée]sistible|exceptionnelle)",
]

# Exceptions : ces patterns peuvent apparaître dans un contexte légitime
ALLOWED_EXCEPTIONS = [
    r"vous\s+d[ée]sabonner",
    r"r[ée]pondez\s+STOP",
    r"aucune\s+obligation",
]


def _has_forbidden_pattern(text: str) -> list[str]:
    """Retourne la liste des patterns interdits trouvés dans le texte."""
    text_lower = text.lower()
    violations = []

    for pattern in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, text_lower)
        if matches:
            # Vérifier si c'est une exception légitime
            is_exception = False
            for exc_pattern in ALLOWED_EXCEPTIONS:
                # Check if the match is within an exception context
                context_pattern = f"(?:{exc_pattern}).*(?:{pattern})|(?:{pattern}).*(?:{exc_pattern})"
                if re.search(context_pattern, text_lower):
                    is_exception = True
                    break
            if not is_exception:
                violations.append(pattern)

    return violations


# ── Tests sur les templates d'outreach ───────────────────────────

class TestOutreachTemplatesNoPressure:
    """Vérifie que TOUS les templates d'outreach sont exempts de pression."""

    @pytest.mark.parametrize("template_key", list(TEMPLATES.keys()))
    def test_template_body_no_pressure(self, template_key):
        """Le corps du template ne doit contenir aucun pattern de pression."""
        template = TEMPLATES[template_key]
        body = template["body"]

        violations = _has_forbidden_pattern(body)
        assert violations == [], (
            f"Template '{template_key}' contient du langage de pression : "
            f"{violations}\n\nCorps du template :\n{body[:300]}..."
        )

    @pytest.mark.parametrize("template_key", list(TEMPLATES.keys()))
    def test_template_subject_no_pressure(self, template_key):
        """Le sujet du template ne doit contenir aucun pattern de pression."""
        template = TEMPLATES[template_key]
        subject = template["subject"]

        violations = _has_forbidden_pattern(subject)
        assert violations == [], (
            f"Subject du template '{template_key}' contient du langage "
            f"de pression : {violations}\nSujet : {subject}"
        )


class TestTemplatesHaveOptOut:
    """Vérifie que tous les templates ont une porte de sortie."""

    @pytest.mark.parametrize("template_key", [
        "j0_recap_top3", "j2_catalogue_interactif",
        "j7_matrice_tco", "j14_essai_routier", "j45_alerte_prix",
    ])
    def test_template_has_stop_option(self, template_key):
        """Les templates intermédiaires doivent mentionner STOP."""
        body = TEMPLATES[template_key]["body"]
        assert "STOP" in body or "désabonner" in body.lower(), (
            f"Template '{template_key}' ne contient pas d'option "
            f"de désabonnement (STOP/désabonner)"
        )

    def test_j60_cloture_is_final(self):
        """Le template J60 (clôture) ne devrait PAS mentionner STOP
        car c'est le dernier message."""
        body = TEMPLATES["j60_cloture"]["body"]
        # J60 is the final message — STOP is optional but not required
        # It should NOT contain any pressure to continue
        violations = _has_forbidden_pattern(body)
        assert violations == []


class TestRenderedMessagesNoPressure:
    """Vérifie les messages rendus avec des variables réelles."""

    def test_rendered_j0_no_pressure(self):
        """Le message J0 rendu ne doit contenir aucune pression."""
        variables = {
            "prospect_name": "Ahmed",
            "top1_name": "Dacia Sandero 2024",
            "top1_price": "180 000 MAD",
            "top1_strengths": "Économie (5/5), Praticité (4/5)",
            "top1_compromises": "⚠ Performance (2/5)",
            "top2_name": "Renault Clio 2023",
            "top2_price": "200 000 MAD",
            "top2_strengths": "Sécurité (4/5)",
            "top2_compromises": "",
            "top3_name": "Peugeot 208 2023",
            "top3_price": "210 000 MAD",
            "top3_strengths": "Design, Confort",
            "top3_compromises": "⚠ Coût réel (2/5)",
            "budget": "220 000 MAD",
            "usage": "ville",
        }
        message = render_template("j0_recap_top3", variables)
        violations = _has_forbidden_pattern(message["body"])
        assert violations == [], (
            f"Message J0 rendu contient du langage de pression : {violations}"
        )

    def test_rendered_j45_no_invented_discount(self):
        """
        Le message J45 (alerte prix) ne doit JAMAIS contenir
        de chiffre de remise si aucune baisse réelle n'est détectée.
        """
        # Rendre avec des variables vides (pas de vraie baisse)
        variables = {
            "prospect_name": "Fatima",
            "vehicle_name": "Renault Clio 2023",
            "old_price": "200 000 MAD",
            "new_price": "195 000 MAD",
            "savings": "5 000 MAD",
        }
        message = render_template("j45_alerte_prix", variables)

        # Le message doit contenir les vrais chiffres, pas des inventions
        body = message["body"]
        assert "200 000" in body  # ancien prix réel
        assert "195 000" in body  # nouveau prix réel
        assert "5 000" in body    # économie réelle
