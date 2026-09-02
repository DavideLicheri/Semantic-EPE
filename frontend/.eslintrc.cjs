module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
  },
  plugins: ['@typescript-eslint', 'react-hooks'],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  rules: {
    // Le prop non usate su interfacce/funzioni sono comuni in componenti React
    // (props ricevute ma non ancora usate) -- avviso, non errore bloccante.
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    // Downgrade a warning (02/09/2026, decisione di Davide): il codebase ha
    // 123 usi preesistenti di `any` (soprattutto services/api.ts, types/*.ts),
    // mai stati sotto lint prima d'ora. Come `error` bloccherebbe sempre
    // `npm run lint` finche' non vengono sistemati tutti -- lavoro corposo,
    // non fatto oggi. Come `warn` il lint segnala i nuovi `any` senza bloccare
    // sul debito esistente.
    '@typescript-eslint/no-explicit-any': 'warn',
  },
}
