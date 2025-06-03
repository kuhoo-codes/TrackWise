const swaggerConfig = {
    openapi: '3.0.0',
    info: {
        title: 'TrackWise API',
        description: `
A timeline-powered portfolio and progress tracker for visualizing career growth.

## Features
* Create new items with names and descriptions
* Retrieve a list of all items
* More features coming soon!
        `,
        version: '1.0.0',
        contact: {
            name: 'TrackWise Support',
            url: 'https://github.com/yourusername/trackwise'
        },
        license: {
            name: 'MIT'
        }
    },
    servers: [
        {
            url: 'http://localhost:8000',
            description: 'Development server'
        }
    ],
    tags: [
        {
            name: 'Items',
            description: 'Item management endpoints'
        },
        {
            name: 'Health Check',
            description: 'API health check endpoints'
        }
    ]
};

module.exports = swaggerConfig; 