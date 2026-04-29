import { useEffect, useState } from 'react';
import OrderForm from './OrderForm';

interface DashboardProps {
  onLogout: () => void;
}

interface AssetPerformance {
  ticker: string;
  quantity: number;
  average_price: number;
  realized_profit: number;
  receipt_url?: string;
}

interface PerformanceResponse {
  investor_name: string;
  total_realized_profit: number;
  assets_performance: AssetPerformance[];
}

interface AssetSummary {
  ticker: string;
  total_quantity: number;
  average_price: number;
  total_invested: number;
}

interface SummaryResponse {
  investor_name: string;
  total_portfolio_value: number;
  assets: AssetSummary[];
}

export default function Dashboard({onLogout}: DashboardProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'performance' | 'statement'>('summary');
  const [summaryData, setSummaryData] = useState<SummaryResponse | null>(null);
  const [performanceData, setPerformanceData] = useState<PerformanceResponse | null>(null);
  const [statementData, setStatementData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAllData = async () => {
    // setLoading(true);
    const token = localStorage.getItem('access_token');
    const headers = { 'Authorization': `Bearer ${token}` };
    
    try {
      const [summaryRes, perfRes, statementRes] = await Promise.all([
        fetch(`${import.meta.env.VITE_API_URL}/portfolio/summary`, { headers }),
        fetch(`${import.meta.env.VITE_API_URL}/portfolio/performance`, { headers }),
        fetch(`${import.meta.env.VITE_API_URL}/transactions/me`, { headers })
      ]);

      if (summaryRes.ok && perfRes.ok && statementRes.ok) {
        setSummaryData(await summaryRes.json());
        setPerformanceData(await perfRes.json());
        setStatementData(await statementRes.json());
      }
    } catch (error) {
      console.error("Erro ao buscar dados do servidor:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  if (loading) return <div className="flex h-screen items-center justify-center font-semibold text-slate-600">Sincronizando com a B3...</div>;

  const investorName = summaryData?.investor_name || performanceData?.investor_name || "Investidor";

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        
        {/* CABECALHO */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800">Olá, {investorName}</h1>
            <p className="text-slate-500">Acompanhe a evolução do seu patrimônio.</p>
          </div>
          <div className="rounded-xl bg-white p-6 shadow-sm border-l-4 border-blue-500">
            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Patrimônio Atual</p>
            <p className="text-2xl font-bold text-blue-600">R$ {Number(summaryData?.total_portfolio_value || 0).toFixed(2)}</p>
          </div>
        </div>

        {/* NAVEGAÇÃO DE ABAS*/}
        <div className="mb-6 flex space-x-1 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'summary' 
                ? 'border-b-2 border-blue-600 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            📊 Posição da Carteira (Resumo)
          </button>
          <button
            onClick={() => setActiveTab('performance')}
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'performance' 
                ? 'border-b-2 border-blue-600 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            💸 Ganhos Realizados
          </button>
        {/* Botao para a aba de historico de ordens */}
        <button
          onClick={() => setActiveTab('statement')}
          className={`px-6 py-3 text-sm font-medium transition-colors ${
            activeTab === 'statement' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'
          }`}
        >
          📜 Extrato Detalhado
        </button>
        </div>
      
        <OrderForm onOrderSuccess={fetchAllData} />

        {/* ABA DE RESUMO */}
        {activeTab === 'summary' && (
          <div className="overflow-hidden rounded-lg bg-white shadow-sm border border-gray-200 animate-in fade-in duration-300">
            <table className="w-full text-left">
              <thead className="bg-slate-800 text-slate-50 text-sm uppercase">
                <tr>
                  <th className="px-6 py-4">Ticker</th>
                  <th className="px-6 py-4 text-center">Quantidade Total</th>
                  <th className="px-6 py-4 text-center">Preço Médio</th>
                  <th className="px-6 py-4 text-center">Total Investido</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {summaryData?.assets?.length === 0 && (
                  <tr><td colSpan={4} className="p-6 text-center text-gray-500">Nenhum ativo na carteira no momento.</td></tr>
                )}
                {summaryData?.assets?.map((asset, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-700">{asset.ticker}</td>
                    <td className="px-6 py-4 text-center">{asset.total_quantity}</td>
                    <td className="px-6 py-4 text-center">R$ {Number(asset.average_price || 0).toFixed(2)}</td>
                    <td className="px-6 py-4 font-semibold text-blue-600 text-center">R$ {Number(asset.total_invested || 0).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ABA DE PERFORMANCE */}
        {activeTab === 'performance' && (
          <div className="overflow-hidden rounded-lg bg-white shadow-sm border border-gray-200 animate-in fade-in duration-300">
            <table className="w-full text-left">
              <thead className="bg-slate-800 text-slate-50 text-sm uppercase">
                <tr>
                  <th className="px-6 py-4">Ticker</th>
                  <th className="px-6 py-4 text-center">Qtd Operada</th>
                  <th className="px-6 py-4 text-center">Preço Médio</th>
                  <th className="px-6 py-4 text-center">Lucro / Prejuízo</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {performanceData?.assets_performance?.length === 0 && (
                  <tr><td colSpan={5} className="p-6 text-center text-gray-500">Nenhuma transação com recibo finalizada.</td></tr>
                )}
                {performanceData?.assets_performance?.map((asset, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-700">{asset.ticker}</td>
                    <td className="px-6 py-4 text-center">{asset.quantity}</td>
                    <td className="px-6 py-4 text-center">R$ {Number(asset.average_price || 0).toFixed(2)}</td>
                    <td className={`px-6 py-4 font-semibold text-center ${(asset.realized_profit || 0) >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      R$ {Number(asset.realized_profit || 0).toFixed(2)}
                    </td>
                    
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      {/* Aba de detalhes das ordens */}
      {activeTab === 'statement' && (
        <div className="overflow-hidden rounded-lg bg-white shadow-sm border border-gray-200">
          <table className="w-full text-left">
            <thead className="bg-slate-800 text-slate-50 text-sm uppercase">
              <tr>
                <th className="px-6 py-4">Data</th>
                <th className="px-6 py-4">Tipo</th>
                <th className="px-6 py-4">Ativo</th>
                <th className="px-6 py-4 text-center">Quantidade</th>
                <th className="px-6 py-4">Preço</th>
                <th className="px-6 py-4">Total</th>
                <th className="px-6 py-4 text-center">Recibo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {statementData.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">{new Date(t.timestamp).toLocaleDateString()}</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-2 py-1 text-xs font-bold ${
                      t.type.toLowerCase() === 'compra' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'
                    }`}>
                      {t.type.toLowerCase() === 'compra' ? 'COMPRA' : 'VENDA'}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-bold">{t.ticker || 'Ativo'}</td>
                  <td className="px-6 py-4 text-center">{t.quantity}</td>
                  <td className="px-6 py-4 text-slate-500">R$ {t.price.toFixed(2)}</td>
                  <td className="px-6 py-4 font-semibold">R$ {(t.quantity * t.price).toFixed(2)}</td>
                  <td className="px-6 py-4 text-center">
                    {t.receipt_url && (
                      <a href={t.receipt_url} target="_blank" className="text-blue-600 hover:underline">
                        📥 Download
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )}

        <button 
          onClick={onLogout} 
          className="text-red-600 hover:text-red-800 font-medium"
        >
          Sair da Conta
        </button>

      </div>
    </div>
  );
}