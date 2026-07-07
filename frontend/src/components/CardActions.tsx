import { Pencil, Trash2 } from 'lucide-react'

interface CardActionsProps {
  onEdit: () => void
  onDelete: () => void
}

export default function CardActions({ onEdit, onDelete }: CardActionsProps) {
  return (
    <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100">
      <button
        onClick={onEdit}
        className="flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium text-kinetix-600 bg-kinetix-50 hover:bg-kinetix-100 rounded-lg transition-colors"
      >
        <Pencil size={15} />
        Редактировать
      </button>
      <button
        onClick={onDelete}
        className="flex items-center justify-center gap-1.5 px-3 py-2 text-sm text-red-500 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
      >
        <Trash2 size={15} />
      </button>
    </div>
  )
}

export function RowActions({ onEdit, onDelete }: CardActionsProps) {
  return (
    <div className="flex gap-1">
      <button onClick={onEdit} className="p-1.5 text-kinetix-600 hover:bg-kinetix-50 rounded" title="Редактировать">
        <Pencil size={16} />
      </button>
      <button onClick={onDelete} className="p-1.5 text-red-400 hover:bg-red-50 rounded" title="Удалить">
        <Trash2 size={16} />
      </button>
    </div>
  )
}
