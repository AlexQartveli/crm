import { Pencil, Trash2 } from 'lucide-react'
import { useI18n } from '../i18n/I18nContext'

interface CardActionsProps {
  onEdit: () => void
  onDelete: () => void
}

export default function CardActions({ onEdit, onDelete }: CardActionsProps) {
  const { t } = useI18n()
  return (
    <div className="flex gap-2 mt-3 pt-3 border-t border-app-border">
      <button
        onClick={onEdit}
        className="flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium rounded-lg transition-colors action-edit"
      >
        <Pencil size={15} />
        {t.common.edit}
      </button>
      <button
        onClick={onDelete}
        className="flex items-center justify-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-colors action-delete"
        title={t.common.delete}
      >
        <Trash2 size={15} />
      </button>
    </div>
  )
}

export function RowActions({ onEdit, onDelete }: CardActionsProps) {
  const { t } = useI18n()
  return (
    <div className="flex gap-1">
      <button onClick={onEdit} className="p-1.5 rounded action-edit-icon" title={t.common.edit}>
        <Pencil size={16} />
      </button>
      <button onClick={onDelete} className="p-1.5 rounded action-delete-icon" title={t.common.delete}>
        <Trash2 size={16} />
      </button>
    </div>
  )
}
