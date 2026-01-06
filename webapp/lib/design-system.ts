/**
 * Unified Design System for SafeEats
 * Ensures consistent styling across all pages
 */

export const colors = {
  primary: 'emerald',
  secondary: 'blue',
  accent: 'purple',
  success: 'emerald',
  warning: 'orange',
  danger: 'red',
  neutral: 'gray',
};

export const spacing = {
  section: 'py-16 sm:py-24',
  containerSmall: 'max-w-2xl',
  containerMedium: 'max-w-4xl',
  containerLarge: 'max-w-6xl',
  padding: 'px-4 sm:px-6 lg:px-8',
};

export const typography = {
  h1: 'text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight',
  h2: 'text-3xl sm:text-4xl font-bold',
  h3: 'text-xl font-semibold',
  h4: 'text-lg font-semibold',
  body: 'text-base text-gray-600',
  bodyLarge: 'text-lg text-gray-600',
};

export const gradient = {
  primary: 'from-emerald-600 to-green-600',
  secondary: 'from-blue-600 to-blue-500',
  light: 'from-emerald-50 via-white to-blue-50',
};

export const buttons = {
  primary: 'px-8 py-4 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all',
  secondary: 'px-8 py-4 border-2 border-emerald-600 text-emerald-600 rounded-lg font-semibold hover:bg-emerald-50 transition-all',
  tertiary: 'px-8 py-4 bg-gray-100 text-gray-900 rounded-lg font-semibold hover:bg-gray-200 transition-all',
  white: 'px-8 py-4 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-all',
  whiteBorder: 'px-8 py-4 border-2 border-white text-white rounded-lg font-semibold hover:bg-white hover:bg-opacity-10 transition-all',
};

export const cards = {
  base: 'p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-all',
  elevated: 'p-8 rounded-xl bg-white shadow-lg hover:shadow-xl transition-all',
  colored: 'p-8 rounded-xl border-2',
};

export const iconSize = 'w-6 h-6';

export const backgrounds = {
  light: 'bg-white',
  muted: 'bg-gray-50',
  gradient: 'bg-gradient-to-br from-gray-50 to-blue-50',
  primary: 'bg-gradient-to-r from-emerald-600 to-green-600',
};
