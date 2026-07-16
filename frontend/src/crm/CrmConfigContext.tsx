import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api, type CrmConfig, type CrmFieldDef } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { useI18n } from '../i18n/I18nContext'
import {
  entityTitle,
  hasModule,
  isFieldHidden,
  listFields,
  ROUTE_MODULE,
} from './helpers'

interface CrmConfigContextValue {
  config: CrmConfig | null
  loading: boolean
  entityLabel: (entity: string, fallback: string) => string
  moduleEnabled: (module: string) => boolean
  routeEnabled: (path: string) => boolean
  fieldHidden: (entity: string, field: string) => boolean
  fieldsFor: (entity: string) => CrmFieldDef[]
  listFieldsFor: (entity: string) => CrmFieldDef[]
}

const CrmConfigContext = createContext<CrmConfigContextValue | null>(null)

export function CrmConfigProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const { locale } = useI18n()
  const [config, setConfig] = useState<CrmConfig | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!user) {
      setConfig(null)
      return
    }
    setLoading(true)
    api.auth.crmConfig()
      .then(setConfig)
      .catch(() => setConfig(null))
      .finally(() => setLoading(false))
  }, [user?.tenant_id, user?.tenant.crm_type])

  const entityLabel = useCallback(
    (entity: string, fallback: string) => entityTitle(config, entity, locale, fallback),
    [config, locale],
  )

  const moduleEnabled = useCallback((module: string) => hasModule(config, module), [config])

  const routeEnabled = useCallback(
    (path: string) => {
      const module = ROUTE_MODULE[path]
      if (!module) return true
      return hasModule(config, module)
    },
    [config],
  )

  const fieldHidden = useCallback(
    (entity: string, field: string) => isFieldHidden(config, entity, field),
    [config],
  )

  const fieldsFor = useCallback(
    (entity: string) => config?.fields[entity] || [],
    [config],
  )

  const listFieldsFor = useCallback(
    (entity: string) => listFields(config, entity),
    [config],
  )

  const value = useMemo(
    () => ({
      config,
      loading,
      entityLabel,
      moduleEnabled,
      routeEnabled,
      fieldHidden,
      fieldsFor,
      listFieldsFor,
    }),
    [config, loading, entityLabel, moduleEnabled, routeEnabled, fieldHidden, fieldsFor, listFieldsFor],
  )

  return <CrmConfigContext.Provider value={value}>{children}</CrmConfigContext.Provider>
}

export function useCrmConfig() {
  const ctx = useContext(CrmConfigContext)
  if (!ctx) throw new Error('useCrmConfig must be used within CrmConfigProvider')
  return ctx
}

export function useCrmLabel(label: { ru: string; en: string; ka: string } | undefined, fallback: string) {
  const { locale } = useI18n()
  if (!label) return fallback
  if (locale === 'en') return label.en
  if (locale === 'ka') return label.ka
  return label.ru
}
