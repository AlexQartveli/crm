export const DEAL_STAGES: Record<string, { label: string; color: string }> = {
  new: { label: 'Новая', color: 'bg-blue-100 text-blue-800' },
  preparation: { label: 'Подготовка', color: 'bg-purple-100 text-purple-800' },
  proposal: { label: 'Предложение', color: 'bg-yellow-100 text-yellow-800' },
  negotiation: { label: 'Переговоры', color: 'bg-orange-100 text-orange-800' },
  won: { label: 'Выиграна', color: 'bg-green-100 text-green-800' },
  lost: { label: 'Проиграна', color: 'bg-red-100 text-red-800' },
}

export const LEAD_STATUSES: Record<string, { label: string; color: string }> = {
  new: { label: 'Новый', color: 'bg-blue-100 text-blue-800' },
  in_progress: { label: 'В работе', color: 'bg-yellow-100 text-yellow-800' },
  converted: { label: 'Конвертирован', color: 'bg-green-100 text-green-800' },
  junk: { label: 'Некачественный', color: 'bg-gray-100 text-gray-800' },
}

export const INVOICE_STATUSES: Record<string, { label: string; color: string }> = {
  draft: { label: 'Черновик', color: 'bg-gray-100 text-gray-800' },
  pending: { label: 'Ожидание', color: 'bg-yellow-100 text-yellow-800' },
  sent: { label: 'Отправлен', color: 'bg-blue-100 text-blue-800' },
  active: { label: 'Активен', color: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Отменён', color: 'bg-red-100 text-red-800' },
  refused: { label: 'Отклонён', color: 'bg-red-100 text-red-800' },
}

export const MOVEMENT_TYPES: Record<string, string> = {
  receipt: 'Приход',
  expense: 'Расход',
  transfer: 'Перемещение',
  adjustment: 'Корректировка',
}

export function formatMoney(amount: number): string {
  return new Intl.NumberFormat('ka-GE', {
    style: 'currency',
    currency: 'GEL',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(date: string): string {
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(date))
}
