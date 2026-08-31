import React from 'react';
import ReactDOM from 'react-dom/client';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { HelmetProvider } from 'react-helmet-async';
import App from './App';

// Protection globale contre les erreurs de removeChild causées par les scripts tiers (Google GSI)
if (typeof Node !== 'undefined' && Node.prototype) {
  const originalRemoveChild = Node.prototype.removeChild;
  Node.prototype.removeChild = function <T extends Node>(child: T): T {
    if (child.parentNode !== this) {
      if (console && console.warn) {
        console.warn('Cannot remove child, not a direct child of this node:', child);
      }
      return child;
    }
    return originalRemoveChild.call(this, child) as T;
  };
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <HelmetProvider>
    <GoogleOAuthProvider clientId="613088379355-vv1j8g19i7svo3iej6rd79u7dt9t73jj.apps.googleusercontent.com">
      <App />
    </GoogleOAuthProvider>
  </HelmetProvider>
);
