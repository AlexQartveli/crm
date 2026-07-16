import { useEffect, useState } from 'react'
import { Building2, User } from 'lucide-react'
import { api, CrmType, TenantRecord } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import Page, { Loading } from '../components/Page'
import { useI18n } from '../i18n/I18nContext'

export default function Cabinet() {
  const { t, locale } = useI18n()
  const { user, refresh } = useAuth()
  const [tab, setTab] = useState<'profile' | 'company'>('profile')
  const [tenant, setTenant] = useState<TenantRecord | null>(null)
  const [crmTypes, setCrmTypes] = useState<CrmType[]>([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [profile, setProfile] = useState({ full_name: '', email: '' })
  const [company, setCompany] = useState({ name: '', email: '', phone: '', address: '' })
  const [passwords, setPasswords] = useState({ current: '', next: '' })

  const canEditCompany = user?.role === 'admin' || user?.role === 'director'

  useEffect(() => {
    Promise.all([
      api.tenant.get(),
      api.auth.crmTypes(),
      user ? Promise.resolve(user) : api.auth.me(),
    ])
      .then(([tnt, types, me]) => {
        setTenant(tnt)
        setCrmTypes(types)
        setProfile({ full_name: me.full_name, email: me.email || '' })
        setCompany({ name: tnt.name, email: tnt.email || '', phone: tnt.phone || '', address: tnt.address || '' })
      })
      .finally(() => setLoading(false))
  }, [user])

  if (loading) return <Loading />

  const crmTypeLabel = (() => {
    const type = crmTypes.find((c) => c.id === tenant?.crm_type)
    if (!type) return tenant?.crm_type || t.common.dash
    if (locale === 'en') return type.label_en
    if (locale === 'ka') return type.label_ka
    return type.label_ru
  })()

  const crmServices = crmTypes.find((c) => c.id === tenant?.crm_type)?.services || []

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.auth.updateProfile(profile)
    await refresh()
    setMessage(t.cabinet.profileSaved)
  }

  const saveCompany = async (e: React.FormEvent) => {
    e.preventDefault()
    const updated = await api.tenant.update(company)
    setTenant(updated)
    setMessage(t.cabinet.companySaved)
  }

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.auth.changePassword(passwords.current, passwords.next)
    setPasswords({ current: '', next: '' })
    setMessage(t.cabinet.passwordChanged)
  }

  return (
    <Page title={t.cabinet.title}>
      <p className="text-app-text-muted mb-6 -mt-2">{t.cabinet.subtitle}</p>

      {message && <div className="mb-4 info-banner-neutral text-sm">{message}</div>}

      <div className="flex gap-2 mb-6">
        <button
          className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 ${tab === 'profile' ? 'bg-kinetix-600 text-white' : 'bg-app-surface'}`}
          onClick={() => setTab('profile')}
        >
          <User size={16} /> {t.cabinet.profileTab}
        </button>
        <button
          className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 ${tab === 'company' ? 'bg-kinetix-600 text-white' : 'bg-app-surface'}`}
          onClick={() => setTab('company')}
        >
          <Building2 size={16} /> {t.cabinet.companyTab}
        </button>
      </div>

      {tab === 'profile' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <form onSubmit={saveProfile} className="card p-6 space-y-4">
            <h2 className="font-semibold">{t.cabinet.profileTab}</h2>
            <div><label className="label">{t.common.name}</label><input className="input" value={profile.full_name} onChange={(e) => setProfile({ ...profile, full_name: e.target.value })} /></div>
            <div><label className="label">{t.common.email}</label><input className="input" type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} /></div>
            <div><label className="label">{t.auth.username}</label><input className="input" value={user?.username || ''} disabled /></div>
            <button type="submit" className="btn-primary">{t.common.save}</button>
          </form>

          <form onSubmit={changePassword} className="card p-6 space-y-4">
            <h2 className="font-semibold">{t.cabinet.changePassword}</h2>
            <div><label className="label">{t.cabinet.currentPassword}</label><input className="input" type="password" value={passwords.current} onChange={(e) => setPasswords({ ...passwords, current: e.target.value })} required /></div>
            <div><label className="label">{t.cabinet.newPassword}</label><input className="input" type="password" value={passwords.next} onChange={(e) => setPasswords({ ...passwords, next: e.target.value })} required minLength={4} /></div>
            <button type="submit" className="btn-primary">{t.cabinet.changePassword}</button>
          </form>
        </div>
      )}

      {tab === 'company' && tenant && (
        <form onSubmit={saveCompany} className="card p-6 space-y-4 max-w-xl">
          <h2 className="font-semibold">{t.cabinet.companyTab}</h2>
          <div><label className="label">{t.auth.crmType}</label><input className="input" value={crmTypeLabel} disabled /></div>
          {crmServices.length > 0 && (
            <div>
              <label className="label">{t.auth.includedServices}</label>
              <ul className="text-sm text-app-text-muted space-y-1 mt-1">
                {crmServices.map((s) => (
                  <li key={s.id}>✓ {locale === 'en' ? s.label_en : locale === 'ka' ? s.label_ka : s.label_ru}</li>
                ))}
              </ul>
            </div>
          )}
          <div><label className="label">{t.auth.companyCode}</label><input className="input" value={tenant.slug} disabled /></div>
          <div><label className="label">{t.auth.companyName}</label><input className="input" value={company.name} disabled={!canEditCompany} onChange={(e) => setCompany({ ...company, name: e.target.value })} /></div>
          <div><label className="label">{t.common.email}</label><input className="input" type="email" value={company.email} disabled={!canEditCompany} onChange={(e) => setCompany({ ...company, email: e.target.value })} /></div>
          <div><label className="label">{t.common.phone}</label><input className="input" value={company.phone} disabled={!canEditCompany} onChange={(e) => setCompany({ ...company, phone: e.target.value })} /></div>
          <div><label className="label">{t.common.address}</label><textarea className="input" rows={2} value={company.address} disabled={!canEditCompany} onChange={(e) => setCompany({ ...company, address: e.target.value })} /></div>
          {canEditCompany && <button type="submit" className="btn-primary">{t.common.save}</button>}
        </form>
      )}
    </Page>
  )
}
