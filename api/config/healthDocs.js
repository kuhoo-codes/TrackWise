const healthDocs = {
    '/': {
        get: {
            tags: ['Health Check'],
            summary: 'Health Check Endpoint',
            description: 'Returns a simple message to confirm the API is running.',
            operationId: 'healthCheck',
            responses: {
                '200': {
                    description: 'API is running successfully',
                    content: {
                        'application/json': {
                            schema: {
                                type: 'object',
                                properties: {
                                    message: {
                                        type: 'string',
                                        example: 'FastAPI with PostgreSQL is running on Mac!'
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

module.exports = healthDocs; 