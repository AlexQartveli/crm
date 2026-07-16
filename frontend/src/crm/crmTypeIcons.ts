import {
  Briefcase,
  GraduationCap,
  Factory,
  ShoppingBag,
  Hotel,
  HardHat,
  Wheat,
  Stethoscope,
  Truck,
  Users,
  type LucideIcon,
} from 'lucide-react'

export const CRM_TYPE_ICONS: Record<string, LucideIcon> = {
  briefcase: Briefcase,
  'graduation-cap': GraduationCap,
  factory: Factory,
  'shopping-bag': ShoppingBag,
  hotel: Hotel,
  'hard-hat': HardHat,
  wheat: Wheat,
  stethoscope: Stethoscope,
  truck: Truck,
  users: Users,
}

export function crmTypeIcon(name: string): LucideIcon {
  return CRM_TYPE_ICONS[name] ?? Briefcase
}
