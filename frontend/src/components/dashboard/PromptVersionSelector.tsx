interface PromptVersion {
  version: string;
  is_default: boolean;
}

interface Props {
  versions: PromptVersion[];
  selectedVersion: string;
  onVersionChange: (version: string) => void;
}

export default function PromptVersionSelector({ versions, selectedVersion, onVersionChange }: Props) {
  return (
    <div className="flex items-center space-x-3">
      <label className="text-sm font-medium text-gray-700">
        Prompt Version:
      </label>
      <select
        value={selectedVersion}
        onChange={(e) => onVersionChange(e.target.value)}
        className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      >
        {versions.map((v) => (
          <option key={v.version} value={v.version}>
            {v.version} {v.is_default && '(default)'}
          </option>
        ))}
      </select>
    </div>
  );
}
