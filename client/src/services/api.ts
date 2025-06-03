interface Item {
  id: number;
  name: string;
  description?: string;
}

export const api = {
  // Get all items
  getItems: async (): Promise<Item[]> => {
    const response = await fetch('/api/items');
    if (!response.ok) {
      throw new Error('Failed to fetch items');
    }
    return response.json();
  },

  // Create a new item
  createItem: async (item: Omit<Item, 'id'>): Promise<Item> => {
    const response = await fetch('/api/items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(item),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create item');
    }
    return response.json();
  },
}; 