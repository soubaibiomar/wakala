/**
 * main.tsx — Point d'entrée React.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { HelmetProvider } from 'react-helmet-async';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <GoogleOAuthProvider clientId="613088379355-vv1j8g19i7svo3iej6rd79u7dt9t73jj.apps.googleusercontent.com">
        <App />
      </GoogleOAuthProvider>
    </HelmetProvider>
  </React.StrictMode>
);
