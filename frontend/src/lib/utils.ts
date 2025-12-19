/**
 * ============================================================================
 * UTILS.TS - Utilitaires généraux
 * ============================================================================
 * Description: Fonctions utilitaires pour le frontend.
 * 
 * Fonctions:
 * - cn: Fusion de classes CSS avec tailwind-merge
 * - formatDate: Formatage de dates
 * - getRiskColor: Couleur selon le niveau de risque
 * ============================================================================
 */

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Fusionne les classes CSS avec support de Tailwind.
 * Utilise clsx pour la logique conditionnelle et tailwind-merge pour éviter les conflits.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Formate une date ISO en format lisible.
 */
export function formatDate(isoString: string): string {
  const date = new Date(isoString)
  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date)
}

/**
 * Retourne la couleur Tailwind selon le niveau de risque.
 */
export function getRiskColor(riskLevel: string): string {
  switch (riskLevel.toLowerCase()) {
    case 'high':
      return 'text-red-600 bg-red-50 border-red-200'
    case 'medium':
      return 'text-orange-600 bg-orange-50 border-orange-200'
    case 'low':
      return 'text-green-600 bg-green-50 border-green-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

/**
 * Retourne la couleur du badge selon le niveau de risque.
 */
export function getRiskBadgeColor(riskLevel: string): string {
  switch (riskLevel.toLowerCase()) {
    case 'high':
      return 'bg-red-500'
    case 'medium':
      return 'bg-orange-500'
    case 'low':
      return 'bg-green-500'
    default:
      return 'bg-gray-500'
  }
}

/**
 * Formate un nombre avec séparateurs de milliers.
 */
export function formatNumber(num: number, decimals: number = 0): string {
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(num)
}
