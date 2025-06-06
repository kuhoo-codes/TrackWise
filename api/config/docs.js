const swaggerConfig = require('./swagger');
const itemDocs = require('./itemDocs');
const healthDocs = require('./healthDocs');

const docs = {
    ...swaggerConfig,
    paths: {
        ...healthDocs,
        ...itemDocs
    },
    components: {
        schemas: {
            Item: {
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
            },
            Error: {
                type: 'object',
                properties: {
                    detail: {
                        type: 'string',
                        description: 'Error message',
                        example: 'Error message details'
                    }
                }
            }
        }
    }
};

module.exports = docs; 