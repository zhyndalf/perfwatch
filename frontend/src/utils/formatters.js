/**
 * Shared formatting utilities for the PerfWatch frontend.
 * Consolidates formatting functions used across Dashboard.vue and History.vue.
 */

/**
 * Format a number with specified decimal places.
 * @param {number|null|undefined} value - The value to format
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string|null} Formatted number or null if invalid
 */
export function formatNumber(value, decimals = 1) {
  if (value === null || value === undefined) return null
  return Number(value).toFixed(decimals)
}

/**
 * Format bytes into human-readable format (B, KB, MB, GB, TB).
 * @param {number|null|undefined} value - Byte value to format
 * @returns {string} Formatted string or 'N/A' if invalid
 */
export function formatBytes(value) {
  if (value === null || value === undefined) return 'N/A'
  const bytes = Number(value)
  if (Number.isNaN(bytes)) return 'N/A'
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  const num = bytes / 1024 ** i
  return `${num.toFixed(num >= 10 ? 0 : 1)} ${units[i]}`
}

/**
 * Format kilobytes into human-readable format (KB, MB, GB).
 * @param {number|null|undefined} value - Kilobyte value to format
 * @returns {string} Formatted string or 'N/A' if invalid
 */
export function formatKB(value) {
  if (value === null || value === undefined) return 'N/A'
  const kb = Number(value)
  if (Number.isNaN(kb)) return 'N/A'
  if (kb === 0) return '0 KB'
  if (kb < 1024) return kb.toFixed(1) + ' KB'
  if (kb < 1024 * 1024) return (kb / 1024).toFixed(1) + ' MB'
  return (kb / (1024 * 1024)).toFixed(1) + ' GB'
}

/**
 * Format bytes per second as throughput.
 * @param {number|null|undefined} value - Bytes per second value
 * @returns {string} Formatted throughput string
 */
export function formatThroughput(value) {
  if (value === null || value === undefined) return '0 B/s'
  return `${formatBytes(value)}/s`
}

/**
 * Format throughput for axis labels (compact format without space).
 * @param {number|null|undefined} value - Bytes value
 * @returns {string} Formatted label string
 */
export function formatThroughputLabel(value) {
  const formatted = formatBytes(value)
  if (formatted === 'N/A') return formatted
  return formatted.replace(' ', '') + '/s'
}

/**
 * Format a perf event entry with value and optional unit.
 * @param {Object|null|undefined} entry - Perf event entry with value and unit
 * @returns {string} Formatted perf value or 'N/A'
 */
export function formatPerfValue(entry) {
  if (!entry || entry.value === null || entry.value === undefined) return 'N/A'
  const value = Number(entry.value)
  if (Number.isNaN(value)) return 'N/A'
  const decimals = Number.isInteger(value) ? 0 : 2
  const unit = entry.unit ? ` ${entry.unit}` : ''
  return `${value.toFixed(decimals)}${unit}`
}

/**
 * Format a perf event value with optional unit (for History view).
 * @param {number|null|undefined} value - Numeric value
 * @param {string|null|undefined} unit - Optional unit string
 * @returns {string} Formatted value or 'N/A'
 */
export function formatPerfValueWithUnit(value, unit) {
  const number = Number(value)
  if (Number.isNaN(number)) return 'N/A'
  const decimals = Number.isInteger(number) ? 0 : 2
  const suffix = unit ? ` ${unit}` : ''
  return `${number.toFixed(decimals)}${suffix}`
}
