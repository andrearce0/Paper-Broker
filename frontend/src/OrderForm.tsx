import React, { useState, useEffect } from 'react';
import api from './services/api';

interface Asset {
  id: number;
  ticker: string;
  name: string;
}

export default function OrderForm({ onOrderSuccess }: { onOrderSuccess: () => void }) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [assetId, setAssetId] = useState('');
  const [type, setType] = useState<'compra' | 'venda'>('compra');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);

  // Busca os ativos para o Dropdown
  useEffect(() => {
    const fetchAssets = async () => {
  try {
    const response = await api.get('/assets/');
    setAssets(response.data);
  } catch (error) {
    console.error("Erro ao carregar ativos", error);
  }
  };
    fetchAssets();
  }, []);

  useEffect(() => {
  const fetchPrice = async () => {
    if (!assetId) return; 

    const selectedAsset = assets.find(a => a.id.toString() === assetId);
    if (!selectedAsset) return;

    try {
      setPrice('Buscando...'); 
      
      const response = await api.get(`/assets/${selectedAsset.ticker}/price`);
      
      setPrice(response.data.price.toString()); 
      
    } catch (error) {
      console.error("Erro ao buscar cotação:", error);
      setPrice('');
    }
  };

  fetchPrice();
}, [assetId, assets]);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);

  try {
    await api.post('/transactions/', {
      asset_id: parseInt(assetId),
      type: type,
      quantity: parseFloat(quantity),
      price: parseFloat(price)
    });


    alert("Ordem executada com sucesso!");
    
    setAssetId(''); 
    setQuantity('');
    setPrice('');
    setType('compra'); 
    onOrderSuccess(); 

  } catch (error: any) {
    console.error("Erro na transação:", error);
    
    const errorMsg = error.response?.data?.detail || "Erro ao executar ordem.";
    alert(errorMsg);
  } finally {
    setLoading(false);
  }
};
  const orderTotal = (parseFloat(price) || 0) * (parseFloat(quantity) || 0);
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
      <h2 className="text-lg font-bold text-slate-800 mb-4">Nova Ordem de Negociação</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
        
        {/* Selecao do Ativo */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Ativo</label>
          <select 
            required
            value={assetId}
            onChange={(e) => setAssetId(e.target.value)}
            className="w-full p-2 border rounded-md bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="">Selecione...</option>
            {assets.map(a => <option key={a.id} value={a.id}>{a.ticker} - {a.name}</option>)}
          </select>
        </div>

        {/* Tipo: Compra ou Venda */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Operação</label>
          <div className="flex bg-gray-100 rounded-md p-1">
            <button 
              type="button"
              onClick={() => setType('compra')}
              className={`flex-1 py-1 text-xs font-bold rounded ${type === 'compra' ? 'bg-blue-600 text-white shadow' : 'text-gray-500'}`}
            >COMPRA</button>
            <button 
              type="button"
              onClick={() => setType('venda')}
              className={`flex-1 py-1 text-xs font-bold rounded ${type === 'venda' ? 'bg-orange-600 text-white shadow' : 'text-gray-500'}`}
            >VENDA</button>
          </div>
        </div>

        {/* Quantidade */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Quantidade</label>
          <input 
            type="number" required value={quantity} onChange={(e) => setQuantity(e.target.value)}
            className="w-full p-2 border rounded-md bg-gray-50 outline-none" placeholder="0"
          />
        </div>

        {/* Preco Unitario */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Preço Mercado (R$)</label>
          <input 
            type="text" 
            required 
            value={price} 
            readOnly
            className={`w-full p-2 border rounded-md outline-none cursor-not-allowed ${
              price === 'Buscando...' ? 'bg-yellow-50 text-yellow-600 animate-pulse' : 'bg-gray-100 text-gray-700 font-semibold'
            }`} 
            placeholder="Selecione um ativo..."
          />
        </div>

          {/* AREA DE RESUMO E ACAO --- */}
        <div className="flex flex-col justify-end w-full">
          <div className="flex justify-between items-end mb-1 px-1 h-4">
            <span className="text-[10px] font-bold text-gray-400 uppercase">Total</span>
            <span className="text-xs font-bold text-blue-600">
              {orderTotal > 0 ? `R$ ${orderTotal.toFixed(2)}` : '--'}
            </span>
          </div>
          
          <button 
            disabled={loading}
            className={`w-full py-2 rounded-md font-bold text-white transition-all shadow-sm ${
              type === 'compra' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-orange-600 hover:bg-orange-700'
            } disabled:opacity-50`}
          >
            {loading ? 'Process...' : 'Executar'}
          </button>
        </div>
      </form>
    </div>
  );
}