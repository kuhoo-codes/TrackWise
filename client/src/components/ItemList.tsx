import { useState, useEffect } from 'react';
import { api } from '../services/api';

interface Item {
  id: number;
  name: string;
  description: string;
}

export default function ItemList() {
  const [items, setItems] = useState<Item[]>([]);
  const [newItem, setNewItem] = useState({ name: '', description: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await api.getItems();
      setItems(response);
      setError(null);
    } catch (err) {
      setError('Failed to fetch items');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.createItem(newItem);
      setNewItem({ name: '', description: '' });
      await fetchItems();
      setError(null);
    } catch (err) {
      setError('Failed to create item');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center">
      {/* Add Item Form */}
      <div className="w-full mb-16">
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
          <div className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm text-gray-500 mb-2 text-center">
                Name
              </label>
              <input
                id="name"
                type="text"
                placeholder="Enter item name"
                value={newItem.name}
                onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                className="w-full px-6 py-3 text-gray-900 bg-white border border-gray-200 rounded-lg focus:border-gray-900 focus:ring-2 focus:ring-gray-900 focus:ring-opacity-20 focus:outline-none transition-all duration-200 text-center shadow-sm hover:border-gray-300"
                required
              />
            </div>
            <div>
              <label htmlFor="description" className="block text-sm text-gray-500 mb-2 text-center">
                Description
              </label>
              <input
                id="description"
                type="text"
                placeholder="Enter description"
                value={newItem.description}
                onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                className="w-full px-6 py-3 text-gray-900 bg-white border border-gray-200 rounded-lg focus:border-gray-900 focus:ring-2 focus:ring-gray-900 focus:ring-opacity-20 focus:outline-none transition-all duration-200 text-center shadow-sm hover:border-gray-300"
              />
            </div>
            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-3 text-sm text-center text-white bg-gray-900 rounded-full hover:bg-gray-800 focus:outline-none disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {loading ? 'Adding...' : 'Add New Item'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="w-full max-w-2xl mx-auto mb-8">
          <div className="px-4 py-3 text-sm text-red-600 bg-red-50 rounded-lg text-center">
            {error}
          </div>
        </div>
      )}

      {/* Items List */}
      <div className="w-full max-w-4xl mx-auto">
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2">
          {items.map((item) => (
            <div
              key={item.id}
              className="p-8 bg-white rounded-xl hover:bg-gray-50 transition-all duration-200 border border-gray-100 shadow-sm hover:shadow-md group"
            >
              <div className="flex flex-col items-center space-y-3">
                <div className="text-center flex-1 w-full">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-gray-700">{item.name}</h3>
                  {item.description && (
                    <p className="text-base text-gray-500 group-hover:text-gray-600">{item.description}</p>
                  )}
                </div>
                <span className="inline-flex items-center justify-center px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full group-hover:bg-gray-200">
                  #{item.id}
                </span>
              </div>
            </div>
          ))}
        </div>
        {items.length === 0 && !loading && (
          <div className="text-center py-16">
            <p className="text-sm text-gray-500">No items yet. Create your first item above.</p>
          </div>
        )}
      </div>
    </div>
  );
} 