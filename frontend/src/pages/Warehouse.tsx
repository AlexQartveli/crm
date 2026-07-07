import { useEffect, useState } from 'react'
import { api, Stock, Warehouse } from '../api/client'

export default function WarehousePage() {
  const [stocks, setStocks] = useState<Stock[]>([])
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [filter, setFilter] = useState<number>(0)

  const load = () => {
    api.stocks.list(filter ? { warehouse_id: filter } : undefined).then(setStocks).catch(console.error)
    api.warehouses.list().then(setWarehouses).catch(console.error)
  }
  useEffect(() => { load() }, [filter])

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Остатки на складе</h1>
        <select
          className="input w-auto"
          value={filter}
          onChange={(e) => setFilter(+e.target.value)}
        >
          <option value={0}>Все склады</option>
          {warehouses.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        {warehouses.map((w) => (
          <div key={w.id} className="card p-5">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-semibold">{w.name}</h3>
              {w.is_default && (
                <span className="text-xs bg-kinetix-100 text-kinetix-700 px-2 py-0.5 rounded-full">Основной</span>
              )}
            </div>
            {w.address && <div className="text-sm text-gray-500">{w.address}</div>}
            <div className="text-sm text-gray-400 mt-2">
              Позиций: {stocks.filter((s) => s.warehouse_id === w.id).length}
            </div>
          </div>
        ))}
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-4 font-medium text-gray-600">Товар</th>
              <th className="text-left p-4 font-medium text-gray-600">Склад</th>
              <th className="text-right p-4 font-medium text-gray-600">Количество</th>
              <th className="text-right p-4 font-medium text-gray-600">Резерв</th>
              <th className="text-right p-4 font-medium text-gray-600">Доступно</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((s) => (
              <tr key={s.id} className="border-b hover:bg-gray-50">
                <td className="p-4 font-medium">{s.product_name}</td>
                <td className="p-4">{s.warehouse_name}</td>
                <td className="p-4 text-right font-medium">{s.quantity}</td>
                <td className="p-4 text-right text-orange-500">{s.reserved}</td>
                <td className="p-4 text-right">
                  <span className={s.available > 0 ? 'text-green-600 font-medium' : 'text-red-500'}>
                    {s.available}
                  </span>
                </td>
              </tr>
            ))}
            {stocks.length === 0 && (
              <tr>
                <td colSpan={5} className="p-8 text-center text-gray-400">Нет остатков</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
