"use client"

declare module "next-themes" {
  import type { ReactNode } from "react"

  export interface ThemeProviderProps {
    attribute?: string
    defaultTheme?: string
    enableSystem?: boolean
    disableTransitionOnChange?: boolean
    storageKey?: string
    themes?: string[]
    forcedTheme?: string
    children?: ReactNode
  }

  export interface UseThemeProps {
    themes?: string[]
    defaultTheme?: string
    storageKey?: string
    forcedTheme?: string
  }

  export interface UseThemeReturn {
    theme: string | undefined
    setTheme: (theme: string) => void
    resolvedTheme: string | undefined
    themes: string[]
    systemTheme: string | undefined
  }

  export function ThemeProvider(props: ThemeProviderProps): React.JSX.Element
  export function useTheme(): UseThemeReturn
}

