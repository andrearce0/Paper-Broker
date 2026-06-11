import React, { useState } from 'react';
import api from './services/api';

export default function OrderForm({ onOrderSuccess }: { onOrderSuccess: () => void }) {
  const [ticker, setTicker] = useState('');
  const [type, setType] = useState<'compra' | 'venda'>('compra');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchingPrice, setSearchingPrice] = useState(false);

  const handleSearchPrice = async () => {
    if (!ticker) return;
    
    setSearchingPrice(true);
    setPrice('Buscando...');
    
    try {
      const response = await api.get(`/assets/${ticker.toUpperCase()}/price`);
      
      setPrice(response.data.price.toString());
      
    } catch (error) {
      console.error("Erro ao buscar cotação:", error);
      alert("Ativo não encontrado no Yahoo Finance. Verifique o código (ex: PETR4.SA)");
      setPrice('');
    } finally {
      setSearchingPrice(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  if (!price || isNaN(parseFloat(price))) {
    alert("Por favor, busque a cotação do ativo antes de executar a ordem.");
    return;
  }

  setLoading(true);

  try {
    const typeToSend = type === 'compra' ? 'BUY' : 'SELL'; 

    // Ajuste feito na linha do 'type'
    await api.post('/transactions/', {
      ticker: ticker.toUpperCase(),
      type: typeToSend,
      quantity: parseFloat(quantity),
      price: parseFloat(price)
    });

    alert("Ordem executada com sucesso!");
    
    setTicker(''); 
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
        
        {/* Input de Texto Dinâmico com Botão de Busca */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Ativo (Ticker)</label>
          <div className="flex gap-2">
            <input 
              type="text" 
              required 
              value={ticker} 
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="Ex: VALE3.SA"
              className="w-full p-2 border rounded-md bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none uppercase"
            />
            <button 
              type="button" 
              onClick={handleSearchPrice}
              disabled={searchingPrice || !ticker}
              className="bg-slate-200 text-slate-700 px-3 rounded-md hover:bg-slate-300 disabled:opacity-50 text-xs font-bold transition-colors"
              title="Buscar Preço Atual"
            >
              {searchingPrice ? '...' : 'BUSCAR'}
            </button>
          </div>
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
            type="number" 
            required 
            min="1" 
            step="1" 
            value={quantity} 
            onChange={(e) => setQuantity(e.target.value)}
            className="w-full p-2 border rounded-md bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="0"
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
            placeholder="Clique em BUSCAR"
          />
        </div>

        {/* AREA DE RESUMO E ACAO */}
        <div className="flex flex-col justify-end w-full">
          <div className="flex justify-between items-end mb-1 px-1 h-4">
            <span className="text-[10px] font-bold text-gray-400 uppercase">Total</span>
            <span className="text-xs font-bold text-blue-600">
              {orderTotal > 0 ? `R$ ${orderTotal.toFixed(2)}` : '--'}
            </span>
          </div>
          
          <button 
            type="submit"
            disabled={loading || !price || isNaN(parseFloat(price))}
            className={`w-full py-2 rounded-md font-bold text-white transition-all shadow-sm ${
              type === 'compra' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-orange-600 hover:bg-orange-700'
            } disabled:opacity-50`}
          >
            {loading ? 'Processando...' : 'Executar'}
          </button>
        </div>
      </form>
    </div>
  );
}