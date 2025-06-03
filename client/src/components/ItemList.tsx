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
    <div>
      {/* Add Item Form */}
      <div className="mb-16">
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
          <div className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm text-gray-500 mb-2">
                Name
              </label>
              <input
                id="name"
                type="text"
                placeholder="Enter item name"
                value={newItem.name}
                onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                className="w-full px-4 py-2 text-gray-900 border-b border-gray-200 focus:border-gray-900 focus:outline-none transition-colors duration-200"
                required
              />
            </div>
            <div>
              <label htmlFor="description" className="block text-sm text-gray-500 mb-2">
                Description
              </label>
              <input
                id="description"
                type="text"
                placeholder="Enter description"
                value={newItem.description}
                onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                className="w-full px-4 py-2 text-gray-900 border-b border-gray-200 focus:border-gray-900 focus:outline-none transition-colors duration-200"
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
        <div className="max-w-2xl mx-auto mb-8">
          <div className="px-4 py-3 text-sm text-red-600 bg-red-50 rounded-lg">
            {error}
          </div>
        </div>
      )}

      {/* Items List */}
      <div className="max-w-4xl mx-auto">
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2">
          {items.map((item) => (
            <div
              key={item.id}
              className="p-6 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-medium text-gray-900">{item.name}</h3>
                  {item.description && (
                    <p className="mt-1 text-sm text-gray-500">{item.description}</p>
                  )}
                </div>
                <span className="text-xs text-gray-400">#{item.id}</span>
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