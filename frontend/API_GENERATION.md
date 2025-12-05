# Type-Safe API Client

## Overview

This project uses **@hey-api/openapi-ts** to auto-generate TypeScript types and API client functions from the FastAPI backend's OpenAPI specification. This ensures type safety between frontend and backend.

## Benefits

✅ **Type Safety** - Compile-time errors if frontend/backend don't match  
✅ **Auto-Sync** - Types automatically reflect backend changes  
✅ **DRY Principle** - Single source of truth (backend schemas)  
✅ **Developer Experience** - IntelliSense for all API endpoints  
✅ **Refactor Safety** - Breaking changes caught at build time  

## Generated Files

```
src/generated/
├── types.gen.ts      # All TypeScript interfaces (ExtractionResult, MedicalData, etc.)
├── sdk.gen.ts        # Typed API functions (uploadDocument, processDocument, etc.)
├── client.gen.ts     # HTTP client configuration
└── client/           # Internal client utilities
```

## How It Works

### 1. Backend Defines Schema (Pydantic)

```python
class MedicalData(BaseModel):
    patient_name: Optional[str] = None
    diagnoses: List[str] = []
    medications: List[str] = []
```

### 2. FastAPI Generates OpenAPI Spec

Available at: http://localhost:8000/openapi.json

### 3. Generate TypeScript Types

```bash
npm run generate:api
```

Creates:
```typescript
export type MedicalData = {
  patient_name?: string | null;
  diagnoses?: Array<string>;
  medications?: Array<string>;
};
```

### 4. Use in Frontend

```typescript
import { processDocument } from './services/api';
import type { ExtractionResult } from './generated/types.gen';

const result: ExtractionResult = await processDocument(docId);
// ✅ Fully typed! IntelliSense works, typos caught at compile time
```

## Workflow

### When Backend API Changes

1. Update Pydantic models in backend
2. Ensure backend is running (`uvicorn app.main:app`)
3. Run `npm run generate:api` in frontend
4. TypeScript will show errors if frontend code needs updates
5. Fix any type errors in components
6. Commit both backend and generated types together

### Example: Adding a New Field

**Backend (`backend/app/models/schemas.py`):**
```python
class MedicalData(BaseModel):
    # ... existing fields
    insurance_provider: Optional[str] = None  # NEW FIELD
```

**Regenerate Types:**
```bash
npm run generate:api
```

**Frontend automatically gets:**
```typescript
export type MedicalData = {
  // ... existing fields
  insurance_provider?: string | null;  // ✅ Auto-added!
};
```

**Update Component:**
```typescript
{medical_data.insurance_provider && (
  <p>Insurance: {medical_data.insurance_provider}</p>
)}
```

## Configuration

Generator config in `package.json`:
```json
{
  "scripts": {
    "generate:api": "openapi-ts --input http://localhost:8000/openapi.json --output src/generated --name client --client fetch --plugins @hey-api/sdk"
  }
}
```

Options:
- `--input`: OpenAPI spec URL or file path
- `--output`: Where to generate files
- `--name`: Base name for generated files
- `--client`: HTTP client to use (fetch, axios, etc.)
- `--plugins`: Additional plugins (SDK generation, etc.)

## Best Practices

✅ **Commit generated files** - Others can build without running backend  
✅ **Regenerate after backend changes** - Keep types in sync  
✅ **Run in CI/CD** - Ensure types match deployed backend  
✅ **Version together** - Generated types should match backend version  
❌ **Don't manually edit generated files** - They'll be overwritten  

## Interview Talking Point

> "I implemented type-safe API communication by auto-generating TypeScript types from the FastAPI OpenAPI schema using @hey-api/openapi-ts. This eliminates manual type maintenance, catches breaking changes at compile time, and ensures the frontend always matches the backend contract. It's a production best practice that reduces bugs and improves developer experience."

## Alternative Tools

- **openapi-typescript** - Types only, no client generation
- **openapi-typescript-codegen** - Similar but older
- **orval** - More complex, supports React Query
- **swagger-codegen** - Java-based, heavyweight

**@hey-api/openapi-ts** is the modern, lightweight choice with excellent TypeScript support.
