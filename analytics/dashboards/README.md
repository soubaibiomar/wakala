# 📊 Dashboards AutoMind

Ce répertoire contient les configurations et exports pour les dashboards
de la couche décisionnelle marketing/économique.

## Outils supportés

- **Metabase** : Dashboards self-hosted connectés à PostgreSQL (Gold layer)
- **Streamlit** : Prototypes interactifs pour l'exploration ML

## Métriques clés

| Métrique                        | Source            |
| ------------------------------- | ----------------- |
| Prix moyen par segment          | Gold / dbt        |
| Taux de conversion              | user_interactions |
| Distribution carburant          | Gold / dbt        |
| Score de confiance vendeurs     | Isolation Forest  |
| Performance recommandation (CTR)| A/B testing       |

## Lancement Streamlit

```bash
cd dashboards
streamlit run app.py
```
