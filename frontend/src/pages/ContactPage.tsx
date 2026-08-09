/**
 * pages/ContactPage.tsx — Page de contact Wakala.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, MapPin, Phone, Send, CheckCircle } from 'lucide-react';
import './StaticPages.css';

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate submission
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 4000);
    setForm({ name: '', email: '', subject: '', message: '' });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <div className="static-page">
      {/* Hero */}
      <section className="static-page__hero">
        <motion.div
          className="static-page__hero-inner"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="static-page__tag">Contact</span>
          <h1 className="static-page__hero-title">
            Parlons <span className="text-gradient">ensemble</span>.
          </h1>
          <p className="static-page__hero-subtitle">
            Une question, une suggestion ou un partenariat ? Notre équipe est à votre écoute.
          </p>
        </motion.div>
      </section>

      {/* Contact Info + Form */}
      <section className="static-page__section">
        <div className="static-page__content">
          <div className="contact-layout">
            {/* Info Cards */}
            <motion.div
              className="contact-info"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <div className="contact-info__card">
                <div className="contact-info__icon">
                  <Mail size={24} />
                </div>
                <div>
                  <h3>Email</h3>
                  <p>contact@wakala.ma</p>
                </div>
              </div>
              <div className="contact-info__card">
                <div className="contact-info__icon">
                  <Phone size={24} />
                </div>
                <div>
                  <h3>Téléphone</h3>
                  <p>+212 5XX-XXXXXX</p>
                </div>
              </div>
              <div className="contact-info__card">
                <div className="contact-info__icon">
                  <MapPin size={24} />
                </div>
                <div>
                  <h3>Adresse</h3>
                  <p>Casablanca, Maroc</p>
                </div>
              </div>
            </motion.div>

            {/* Form */}
            <motion.form
              className="contact-form"
              onSubmit={handleSubmit}
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.15 }}
            >
              {submitted && (
                <div className="contact-form__success">
                  <CheckCircle size={20} />
                  Message envoyé avec succès ! Nous vous répondrons sous 24h.
                </div>
              )}
              <div className="contact-form__row">
                <div className="contact-form__group">
                  <label htmlFor="contact-name">Nom complet</label>
                  <input
                    id="contact-name"
                    name="name"
                    type="text"
                    placeholder="Votre nom"
                    value={form.name}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="contact-form__group">
                  <label htmlFor="contact-email">Email</label>
                  <input
                    id="contact-email"
                    name="email"
                    type="email"
                    placeholder="votre@email.com"
                    value={form.email}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
              <div className="contact-form__group">
                <label htmlFor="contact-subject">Sujet</label>
                <select
                  id="contact-subject"
                  name="subject"
                  value={form.subject}
                  onChange={handleChange}
                  required
                >
                  <option value="">Choisir un sujet</option>
                  <option value="general">Question générale</option>
                  <option value="bug">Signaler un bug</option>
                  <option value="partnership">Partenariat</option>
                  <option value="press">Presse</option>
                  <option value="other">Autre</option>
                </select>
              </div>
              <div className="contact-form__group">
                <label htmlFor="contact-message">Message</label>
                <textarea
                  id="contact-message"
                  name="message"
                  rows={5}
                  placeholder="Décrivez votre demande..."
                  value={form.message}
                  onChange={handleChange}
                  required
                />
              </div>
              <button type="submit" className="contact-form__submit">
                <Send size={18} />
                Envoyer le message
              </button>
            </motion.form>
          </div>
        </div>
      </section>
    </div>
  );
}
