import { defineConfig } from 'wxt';

// See https://wxt.dev/api/config.html
export default defineConfig({
  modules: ['@wxt-dev/module-react'],
  manifest: {
    name: 'Resource Saver',
    description: 'Save articles, YouTube videos, and tools to your personal database',
    version: '1.0.0',
    permissions: ['activeTab'],
    action: {
      default_title: 'Resource Saver',
      default_popup: 'popup.html',
    },
  },
});
