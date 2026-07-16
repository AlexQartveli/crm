import { useI18n } from '../i18n/I18nContext'
import { useCrmConfig } from '../crm/CrmConfigContext'
import { fieldLabel } from '../crm/helpers'
import type { CrmFieldDef } from '../api/client'

interface Props {
  entity: string
  values: Record<string, unknown>
  onChange: (values: Record<string, unknown>) => void
}

function FieldInput({
  field,
  value,
  onChange,
}: {
  field: CrmFieldDef
  value: unknown
  onChange: (v: unknown) => void
}) {
  const { locale } = useI18n()
  const label = fieldLabel(field, locale)
  const strVal = value === undefined || value === null ? '' : String(value)

  if (field.type === 'select') {
    return (
      <div>
        <label className="label">{label}{field.required ? ' *' : ''}</label>
        <select
          className="input"
          required={field.required}
          value={strVal}
          onChange={(e) => onChange(e.target.value || undefined)}
        >
          <option value="">—</option>
          {(field.options || []).map((o) => (
            <option key={o.id} value={o.id}>
              {locale === 'en' ? o.label_en : locale === 'ka' ? o.label_ka : o.label_ru}
            </option>
          ))}
        </select>
      </div>
    )
  }

  if (field.type === 'textarea') {
    return (
      <div>
        <label className="label">{label}{field.required ? ' *' : ''}</label>
        <textarea
          className="input min-h-[80px]"
          required={field.required}
          value={strVal}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    )
  }

  const inputType = field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : field.type === 'email' ? 'email' : 'text'

  return (
    <div>
      <label className="label">{label}{field.required ? ' *' : ''}</label>
      <input
        className="input"
        type={inputType}
        required={field.required}
        value={field.type === 'number' ? (value === undefined || value === null ? '' : Number(value)) : strVal}
        onChange={(e) => onChange(field.type === 'number' ? (e.target.value === '' ? undefined : +e.target.value) : e.target.value)}
      />
    </div>
  )
}

export default function CustomFieldsForm({ entity, values, onChange }: Props) {
  const { fieldsFor } = useCrmConfig()
  const fields = fieldsFor(entity)
  if (!fields.length) return null

  const setField = (key: string, val: unknown) => {
    onChange({ ...values, [key]: val })
  }

  return (
    <div className="border-t border-app-border pt-4 mt-2 space-y-4">
      {fields.map((field) => (
        <FieldInput
          key={field.key}
          field={field}
          value={values[field.key]}
          onChange={(v) => setField(field.key, v)}
        />
      ))}
    </div>
  )
}
