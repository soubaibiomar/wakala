/**
 * pages/LegalPage.tsx — Mentions légales de Wakala.
 */

import { motion } from 'framer-motion';
import './StaticPages.css';

export default function LegalPage() {
  return (
    <div className="static-page">
      {/* Hero */}
      <section className="static-page__hero static-page__hero--compact">
        <motion.div
          className="static-page__hero-inner"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="static-page__tag">Juridique</span>
          <h1 className="static-page__hero-title">Mentions légales</h1>
          <p className="static-page__hero-subtitle">
            Informations légales, politique de confidentialité et conditions d'utilisation.
          </p>
        </motion.div>
      </section>

      {/* Content */}
      <section className="static-page__section">
        <div className="static-page__content static-page__legal">
          <motion.article
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>1. Éditeur du site</h2>
            <p>
              Le site <strong>wakala.ma</strong> est édité par Wakala, plateforme
              de marketplace automobile propulsée par l'intelligence artificielle.
            </p>
            <ul>
              <li><strong>Raison sociale :</strong> Wakala SARL</li>
              <li><strong>Siège social :</strong> Casablanca, Maroc</li>
              <li><strong>Email :</strong> contact@wakala.ma</li>
              <li><strong>Directeur de la publication :</strong> L'équipe Wakala</li>
            </ul>
          </motion.article>

          <motion.article
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>2. Hébergement</h2>
            <p>
              Le site est hébergé par des fournisseurs cloud sécurisés. Les données
              sont stockées dans des centres de données conformes aux normes internationales
              de sécurité.
            </p>
          </motion.article>

          <motion.article
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>3. Propriété intellectuelle</h2>
            <p>
              L'ensemble du contenu du site (textes, images, graphismes, logos,
              icônes, algorithmes, logiciels) est la propriété exclusive de
              Wakala ou de ses partenaires, et est protégé par les lois
              marocaines et internationales relatives à la propriété
              intellectuelle.
            </p>
            <p>
              Toute reproduction, représentation, modification ou distribution,
              totale ou partielle, du contenu du site sans autorisation
              préalable écrite est strictement interdite.
            </p>
          </motion.article>

          <motion.article
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>4. Protection des données personnelles</h2>
            <p>
              Conformément à la loi n° 09-08 relative à la protection des
              personnes physiques à l'égard du traitement des données à caractère
              personnel, Wakala s'engage à protéger la vie privée de ses
              utilisateurs.
            </p>
            <h3>Données collectées</h3>
            <ul>
              <li>Informations d'inscription (nom, email, téléphone)</li>
              <li>Données de navigation et préférences de recherche</li>
              <li>Informations relatives aux annonces publiées</li>
            </ul>
            <h3>Finalités du traitement</h3>
            <ul>
              <li>Gestion des comptes utilisateurs</li>
              <li>Personnalisation des recommandations (IA)</li>
              <li>Calcul des scores de confiance</li>
              <li>Amélioration continue de la plateforme</li>
            </ul>
            <h3>Droits des utilisateurs</h3>
            <p>
              Vous disposez d'un droit d'accès, de rectification, de suppression
              et d'opposition sur vos données personnelles. Pour exercer ces
              droits, contactez-nous à{' '}
              <a href="mailto:contact@wakala.ma">contact@wakala.ma</a>.
            </p>
          </motion.article>

          <motion.article
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>5. Cookies</h2>
            <p>
              Le site utilise des cookies pour améliorer l'expérience utilisateur,
              mémoriser les préférences de recherche et générer des statistiques
              de fréquentation. Vous pouvez configurer votre navigateur pour
              refuser les cookies.
            </p>
          </motion.article>

          <motion.article
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>6. Limitation de responsabilité</h2>
            <p>
              Wakala s'efforce d'assurer l'exactitude des informations publiées
              sur le site. Toutefois, Wakala ne saurait être tenue responsable
              des erreurs, omissions ou résultats qui pourraient découler d'une
              mauvaise utilisation du site.
            </p>
            <p>
              Les scores de confiance et estimations de prix sont fournis à
              titre indicatif et ne constituent pas un engagement contractuel.
            </p>
          </motion.article>

          <motion.article
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2>7. Droit applicable</h2>
            <p>
              Les présentes mentions légales sont soumises au droit marocain.
              Tout litige relatif à l'utilisation du site sera de la compétence
              exclusive des tribunaux de Casablanca.
            </p>
          </motion.article>

          <div className="static-page__legal-updated">
            Dernière mise à jour : Août 2026
          </div>
        </div>
      </section>
    </div>
  );
}
