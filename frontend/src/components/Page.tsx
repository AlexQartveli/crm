import { ReactNode } from 'react'
import { useI18n } from '../i18n/I18nContext'

interface PageProps {
  title: string
  action?: ReactNode
  children: ReactNode
}

export default function Page({ title, action, children }: PageProps) {
  return (
    <div className="p-4 md:p-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <h1 className="text-xl md:text-2xl font-bold">{title}</h1>
        {action}
      </div>
      {children}
    </div>
  )
}

export function TableWrap({ children }: { children: ReactNode }) {
  return (
    <div className="card overflow-x-auto">
      {children}
    </div>
  )
}

export function Loading() {
  const { t } = useI18n()
  return (
    <div className="p-8 flex items-center justify-center">
      <div className="animate-pulse text-gray-400">{t.common.loading}</div>
    </div>
  )
}

export function Empty({ text }: { text: string }) {
  return <div className="p-8 text-center text-gray-400">{text}</div>
}
