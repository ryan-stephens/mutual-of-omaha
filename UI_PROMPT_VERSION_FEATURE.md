# Prompt Version Selector - UI Feature

## 🎯 Feature Overview

Added a **Prompt Version Selector** to the UI, allowing users to choose which prompt version to use for document extraction.

---

## 🖼️ UI Changes

### Before
- Users could only use the default prompt version
- No visibility into which prompt was being used

### After
- **Dropdown selector** above the file upload area
- Shows all available prompt versions with descriptions
- Displays selected prompt version in extraction results

---

## 📍 Location in UI

```
┌─────────────────────────────────────────────┐
│  MedExtract - Extract Page                  │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ Prompt Version                        │  │
│  │ ┌──────────────────────────────────┐ │  │
│  │ │ v2.0.0 - Advanced Normalization ▼│ │  │
│  │ └──────────────────────────────────┘ │  │
│  │ Select which prompt version to use   │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ Drag & drop file or click to upload  │  │
│  └──────────────────────────────────────┘  │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 🔧 Available Prompt Versions

| Version | Description |
|---------|-------------|
| **v1.0.0** | Basic Extraction - Initial prompt template |
| **v1.1.0** | Enhanced Medical Terms - Better medical terminology handling |
| **v2.0.0** | Advanced Normalization - Latest with improved data normalization (default) |

---

## 💻 Code Changes

### 1. HomePage Component (`frontend/src/pages/HomePage.tsx`)

**Added:**
- `promptVersion` state (defaults to `v2.0.0`)
- `PROMPT_VERSIONS` constant with version options
- Dropdown selector UI
- Pass `promptVersion` to `processDocument()` API call

**Key Code:**
```typescript
const [promptVersion, setPromptVersion] = useState('v2.0.0');

// Dropdown UI
<select
  value={promptVersion}
  onChange={(e) => setPromptVersion(e.target.value)}
  disabled={isProcessing}
>
  {PROMPT_VERSIONS.map((version) => (
    <option key={version.value} value={version.value}>
      {version.label}
    </option>
  ))}
</select>

// Pass to API
const extractionResult = await processDocument(
  uploadResponse.document_id,
  promptVersion
);
```

### 2. API Service (`frontend/src/services/api.ts`)

**Updated:**
- `processDocument()` now accepts `promptVersion` parameter
- Sends prompt version in request body

**Key Code:**
```typescript
export const processDocument = async (
  documentId: string,
  promptVersion: string = 'v2.0.0'
): Promise<ExtractionResult> => {
  const { data, error } = await processDocumentApiProcessDocumentIdPost({
    path: { document_id: documentId },
    body: { prompt_version: promptVersion },
  });
  // ...
};
```

### 3. Results Display (`frontend/src/components/ResultsDisplay.tsx`)

**Updated:**
- Shows prompt version used in results header

**Key Code:**
```typescript
{result.prompt_version && (
  <p className="text-sm text-gray-500">
    <span className="font-medium">Prompt Version:</span> {result.prompt_version}
  </p>
)}
```

---

## 🎨 UI/UX Features

### Dropdown Behavior
- ✅ **Disabled during processing** - Prevents changing version mid-extraction
- ✅ **Clear labels** - Each version has descriptive text
- ✅ **Help text** - Explains what the selector does
- ✅ **Accessible** - Proper label association and keyboard navigation

### Visual Design
- Clean, modern dropdown with Tailwind CSS
- Consistent with existing UI design
- Focus states for accessibility
- Disabled state when processing

---

## 🔄 User Workflow

1. **User lands on Extract page**
2. **Selects prompt version** from dropdown (defaults to v2.0.0)
3. **Uploads document** via file picker or drag-and-drop
4. **Document processes** using selected prompt version
5. **Results display** showing which prompt version was used

---

## 🧪 Testing

### Manual Testing Steps

1. **Test version selection:**
   ```
   - Select v1.0.0
   - Upload a document
   - Verify results show "Prompt Version: v1.0.0"
   ```

2. **Test version switching:**
   ```
   - Upload with v1.0.0
   - Change to v2.0.0
   - Upload another document
   - Verify different prompt was used
   ```

3. **Test disabled state:**
   ```
   - Start uploading a document
   - Verify dropdown is disabled during processing
   - Verify dropdown re-enables after completion
   ```

---

## 📊 Backend Integration

The backend already supports prompt versions via the `/api/process/{document_id}` endpoint:

**Request Body:**
```json
{
  "prompt_version": "v2.0.0"
}
```

**Backend Files:**
- `backend/app/routers/process.py` - Accepts `prompt_version` parameter
- `backend/app/services/bedrock_service.py` - Loads prompt from `backend/prompts/{version}.txt`
- `backend/prompts/` - Contains prompt version files

---

## 🎯 Benefits

### For Users
- ✅ **Control** - Choose which prompt to use
- ✅ **Transparency** - See which version was used
- ✅ **Experimentation** - Compare different prompt versions

### For MLOps
- ✅ **A/B Testing** - Users can test different prompts
- ✅ **Metrics** - Track performance by prompt version
- ✅ **Rollback** - Easy to revert to older prompts if needed

### For Development
- ✅ **Testing** - Test new prompts without changing defaults
- ✅ **Debugging** - Isolate prompt-related issues
- ✅ **Iteration** - Quickly test prompt improvements

---

## 🚀 Future Enhancements

Potential improvements:
- **Version comparison** - Side-by-side comparison of results from different prompts
- **Version details** - Show changelog or improvements for each version
- **Recommended version** - Badge indicating "Recommended" or "Latest"
- **Performance metrics** - Show avg processing time/accuracy per version
- **Auto-select** - Remember user's last selected version

---

## 📝 Summary

The prompt version selector gives users full control over which extraction prompt to use, enabling:
- Easy A/B testing
- Transparent prompt versioning
- Better MLOps metrics tracking
- Improved user experience

**Status:** ✅ Implemented and ready to test!

---

**Last Updated:** December 5, 2025  
**Feature:** Prompt Version Selector  
**Files Modified:** 3 (HomePage.tsx, api.ts, ResultsDisplay.tsx)
