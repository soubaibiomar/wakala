import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Analyse de sentiment pour les avis clients.
    Utilise un modèle HuggingFace léger (distilbert ou équivalent multilingue).
    """

    def __init__(self):
        self.analyzer = None

    def load_model(self):
        """Lazy loading du modèle pour éviter de ralentir le démarrage."""
        if self.analyzer is None:
            try:
                # Utilisation d'un modèle multilingue léger adapté pour les avis
                self.analyzer = pipeline(
                    "sentiment-analysis", 
                    model="nlptown/bert-base-multilingual-uncased-sentiment",
                    device=-1 # CPU par défaut
                )
                logger.info("Sentiment analysis model loaded.")
            except Exception as e:
                logger.error(f"Error loading sentiment model: {e}")

    def analyze(self, text: str) -> float:
        """
        Analyse le texte et retourne un score de sentiment entre 0 et 1.
        """
        if not text:
            return 0.5
            
        self.load_model()
        if self.analyzer is None:
            return 0.5 # Neutre si erreur
            
        try:
            # Le modèle retourne des étoiles ("1 star" à "5 stars")
            result = self.analyzer(text[:512])[0]
            label = result['label']
            stars = int(label.split()[0])
            
            # Convertir 1-5 étoiles en score 0-1
            score = (stars - 1) / 4.0
            return round(score, 2)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 0.5

sentiment_analyzer = SentimentAnalyzer()
