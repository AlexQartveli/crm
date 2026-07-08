import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Leads from './pages/Leads'
import Deals from './pages/Deals'
import Contacts from './pages/Contacts'
import Companies from './pages/Companies'
import Products from './pages/Products'
import WarehousePage from './pages/Warehouse'
import Movements from './pages/Movements'
import Accounting from './pages/Accounting'
import TaxSettings from './pages/TaxSettings'
import Inbox from './pages/Inbox'
import Integrations from './pages/Integrations'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="leads" element={<Leads />} />
        <Route path="deals" element={<Deals />} />
        <Route path="contacts" element={<Contacts />} />
        <Route path="companies" element={<Companies />} />
        <Route path="products" element={<Products />} />
        <Route path="warehouse" element={<WarehousePage />} />
        <Route path="movements" element={<Movements />} />
        <Route path="inbox" element={<Inbox />} />
        <Route path="integrations" element={<Integrations />} />
        <Route path="accounting" element={<Accounting />} />
        <Route path="accounting/settings" element={<TaxSettings />} />
      </Route>
    </Routes>
  )
}
