# MedExtract Frontend

React + TypeScript frontend for AI-powered medical document extraction.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS v4** - Styling
- **@hey-api/openapi-ts** - Auto-generated API client

## Setup

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will run at http://localhost:5173

## Type-Safe API Client

This project uses **auto-generated TypeScript types** from the FastAPI backend's OpenAPI schema. This ensures:
- ✅ Type safety between frontend and backend
- ✅ Automatic type updates when backend changes
- ✅ Compile-time error detection for breaking changes

### Regenerate Types

Whenever the backend API changes, regenerate the TypeScript types:

```bash
# Make sure backend is running on port 8000
npm run generate:api
```

This creates:
- `src/generated/types.gen.ts` - TypeScript interfaces
- `src/generated/sdk.gen.ts` - Typed API functions
- `src/generated/client.gen.ts` - HTTP client configuration

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default configuration:
```
VITE_API_URL=http://localhost:8000/api
```

## Project Structure

```
src/
├── components/
│   ├── FileUpload.tsx        # Drag-drop upload component
│   ├── ProcessingStatus.tsx  # Status indicator
│   └── ResultsDisplay.tsx    # Extracted data display
├── services/
│   └── api.ts                # API wrapper (uses generated SDK)
├── generated/                # ⚡ Auto-generated from OpenAPI
│   ├── types.gen.ts          # TypeScript interfaces
│   ├── sdk.gen.ts            # Typed API functions
│   └── client.gen.ts         # HTTP client config
├── App.tsx                   # Main application
└── main.tsx                  # Entry point
```

## Usage

1. **Start Backend**: Ensure FastAPI backend is running on port 8000
2. **Upload Document**: Drag and drop a medical document (TXT, PDF, DOC)
3. **View Results**: Extracted medical data displays automatically

## Building for Production

```bash
npm run build
```

Build output will be in `dist/` folder.
