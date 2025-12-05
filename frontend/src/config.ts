/**
 * Application configuration
 * Supports both local development and production Lambda deployment
 */

export const config = {
  /**
   * API Base URL
   * - Development: Local FastAPI server
   * - Production: AWS API Gateway endpoint
   */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  /**
   * Environment
   */
  environment: import.meta.env.MODE || 'development',
  
  /**
   * Is production deployment
   */
  isProduction: import.meta.env.PROD,
} as const;

export default config;
