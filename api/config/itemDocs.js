const itemDocs = {
    '/api/items': {
        get: {
            tags: ['Items'],
            summary: 'Get All Items',
            description: 'Retrieves a list of all items in the database.',
            operationId: 'getItems',
            responses: {
                '200': {
                    description: 'List of items retrieved successfully',
                    content: {
                        'application/json': {
                            schema: {
                                type: 'array',
                                items: {
                                    type: 'object',
                                    properties: {
                                        id: {
                                            type: 'integer',
                                            description: 'The item ID',
                                            example: 1
                                        },
                                        name: {
                                            type: 'string',
                                            description: 'The name of the item',
                                            example: 'Sample Item'
                                        },
                                        description: {
                                            type: 'string',
                                            description: 'The description of the item',
                                            example: 'This is a sample item description',
                                            nullable: true
                                        }
                                    },
                                    required: ['id', 'name']
                                }
                            }
                        }
                    }
                }
            }
        },
        post: {
            tags: ['Items'],
            summary: 'Create New Item',
            description: 'Creates a new item with the provided name and optional description.',
            operationId: 'createItem',
            requestBody: {
                required: true,
                content: {
                    'application/json': {
                        schema: {
                            type: 'object',
                            properties: {
                                name: {
                                    type: 'string',
                                    description: 'The name of the item',
                                    example: 'New Item'
                                },
                                description: {
                                    type: 'string',
                                    description: 'The description of the item',
                                    example: 'This is a new item description',
                                    nullable: true
                                }
                            },
                            required: ['name']
                        }
                    }
                }
            },
            responses: {
                '201': {
                    description: 'Item created successfully',
                    content: {
                        'application/json': {
                            schema: {
                                type: 'object',
                                properties: {
                                    id: {
                                        type: 'integer',
                                        description: 'The ID of the created item',
                                        example: 1
                                    },
                                    name: {
                                        type: 'string',
                                        description: 'The name of the created item',
                                        example: 'New Item'
                                    },
                                    description: {
                                        type: 'string',
                                        description: 'The description of the created item',
                                        example: 'This is a new item description',
                                        nullable: true
                                    }
                                }
                            }
                        }
                    }
                },
                '400': {
                    description: 'Invalid input',
                    content: {
                        'application/json': {
                            schema: {
                                type: 'object',
                                properties: {
                                    detail: {
                                        type: 'string',
                                        example: 'Invalid request body'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
};

module.exports = itemDocs; 