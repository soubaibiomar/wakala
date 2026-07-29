import re

filepath = "D:/Projet automobile/vente-auto-platform/Livrables/benchmark-concurrentiel.tex"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    r"Utilisation de modèles de régression complexes \(ex\. : XGBoost\) pour évaluer en temps réel la juste valeur d'un véhicule et d'algorithmes d'apprentissage non supervisé \(ex\. : Isolation Forest\) pour la détection de fraudes ou d'anomalies comportementales\.": "Utilisation de modèles d'Intelligence Artificielle (ex. : Qdrant, Neo4j) pour capturer les nuances des besoins de l'utilisateur et proposer une recommandation de véhicules hyper-personnalisée, s'éloignant des simples filtres de recherche classiques.",
    r"souffre d'une forte asymétrie d'information et d'un manque de confiance\.": "souffre d'une forte complexité technique et d'un manque d'accompagnement personnalisé.",
    r"L'absence totale de score de confiance vendeur ou de mécanismes de vérification du véhicule\.": "L'absence totale d'assistance automatisée (Chatbot) pour orienter un acheteur novice.",
    r"Une vulnérabilité critique aux fraudes \(fausses annonces, arnaques aux acomptes, fausses coordonnées\) en raison de l'absence de détection automatique en temps réel\.": "Une expérience utilisateur froide et purement transactionnelle, laissant l'acheteur seul face à la difficulté de trouver le modèle correspondant à son style de vie.",
    r"\\item\[L'absence de détection de fraude et de score de confiance\].*?(?=\\item|\\end\{description\})": r"""\item[L'absence d'accompagnement et de recommandation] : C'est le problème majeur du marché marocain. L'achat de véhicules d'occasion s'accompagne d'une grande difficulté de choix pour les novices. Les plateformes actuelles n'intègrent aucun modèle IA conversationnel ni de moteur de recommandation basé sur le profil de l'utilisateur. La recherche s'effectue uniquement par des filtres techniques arides (année, kilométrage), laissant l'utilisateur final totalement seul pour déduire quel véhicule lui conviendrait le mieux.
    """,
    r"XGBoost, Isolation Forest, Neo4j \(Similarité\)": "Llama, Qdrant (Vectoriel), Neo4j (Graphe)",
    r"Un capital de confiance historique": "Une assise historique",
    r"Une légitimité historique et une confiance des professionnels": "Une légitimité historique auprès des professionnels"
}

for k, v in replacements.items():
    content = re.sub(k, v, content, flags=re.DOTALL)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated benchmark-concurrentiel.tex")
