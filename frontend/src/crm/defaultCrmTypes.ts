import type { CrmType } from '../api/client'

/** Запасной список, если API ещё не обновлён или недоступен. */
export const FALLBACK_CRM_TYPES: CrmType[] = [
  { id: 'general', label_ru: 'Универсальный CRM', label_en: 'Universal CRM', label_ka: 'უნივერსალური CRM', desc_ru: 'Для любого бизнеса', desc_en: 'For any business', desc_ka: 'ნებისმიერი ბიზნესისთვის', icon: 'briefcase', features: [] },
  { id: 'education', label_ru: 'Учебные заведения', label_en: 'Education', label_ka: 'საგანმანათლებლო', desc_ru: 'Школы, колледжи, курсы', desc_en: 'Schools and courses', desc_ka: 'სკოლები და კურსები', icon: 'graduation-cap', features: [] },
  { id: 'factory', label_ru: 'Производство и фабрики', label_en: 'Manufacturing', label_ka: 'წარმოება', desc_ru: 'Заводы и B2B', desc_en: 'Factories and B2B', desc_ka: 'заводები', icon: 'factory', features: [] },
  { id: 'retail', label_ru: 'Розница и магазины', label_en: 'Retail', label_ka: 'საცალო ვაჭრობა', desc_ru: 'Магазины и e-commerce', desc_en: 'Shops', desc_ka: 'მაღაზიები', icon: 'shopping-bag', features: [] },
  { id: 'hospitality', label_ru: 'Отели и туризм', label_en: 'Hotels & tourism', label_ka: 'ტურიზმი', desc_ru: 'Отели, рестораны', desc_en: 'Hotels, restaurants', desc_ka: 'სასტუმროები', icon: 'hotel', features: [] },
  { id: 'construction', label_ru: 'Строительство', label_en: 'Construction', label_ka: 'მშენებლობა', desc_ru: 'Стройкомпании', desc_en: 'Construction firms', desc_ka: 'სამშენებლო', icon: 'hard-hat', features: [] },
  { id: 'agriculture', label_ru: 'Сельское хозяйство', label_en: 'Agriculture', label_ka: 'სოფლის მეურნეობა', desc_ru: 'Фермы, виноделие', desc_en: 'Farms, wine', desc_ka: 'fermebi', icon: 'wheat', features: [] },
  { id: 'medical', label_ru: 'Медицина и клиники', label_en: 'Medical', label_ka: 'мedicina', desc_ru: 'Клиники, записи', desc_en: 'Clinics', desc_ka: 'кlinikebi', icon: 'stethoscope', features: [] },
  { id: 'logistics', label_ru: 'Логистика', label_en: 'Logistics', label_ka: 'ლოგისტика', desc_ru: 'Перевозки', desc_en: 'Freight', desc_ka: 'грузоперевозки', icon: 'truck', features: [] },
  { id: 'services', label_ru: 'Услуги и агентства', label_en: 'Services', label_ka: 'სერვისები', desc_ru: 'Консалтинг, IT', desc_en: 'Consulting, IT', desc_ka: 'сервисы', icon: 'users', features: [] },
]
