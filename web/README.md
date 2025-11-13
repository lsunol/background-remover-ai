# Web Frontend

Vue 3 + Tailwind CSS frontend for Background Remover AI.

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Access at http://localhost:5173

## Build for Production

```bash
# Build static files
npm run build
```

Output will be in `/dist` directory, which is served by FastAPI.

## Features

- Drag & drop image upload
- Side-by-side model comparison
- Transparent background visualization
- Rate limiting (5 requests/hour)
- Mobile responsive
