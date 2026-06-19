import { readFileSync, writeFileSync, unlinkSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { strict as assert } from 'assert';

const __filename = fileURLToPath(import.meta.url);
const __dirname = resolve(dirname(__filename));

const AppPath = resolve(__dirname, '..', 'App.tsx');
let originalContent: string;

// Load original content once
try {
  originalContent = readFileSync(AppPath, 'utf-8');
} catch (err) {
  console.error('Failed to read App.tsx:', err);
  process.exit(1);
}

// Since we are not using a test framework, we'll just run checks and throw on failure
try {
  // Happy path: Upload is imported from lucide-react
  const content = readFileSync(AppPath, 'utf-8');
  const importPattern = /import\s*{[\s\S]*?Upload[\s\S]*?}\s+from\s+['"]lucide-react['"];/;
  assert.ok(importPattern.test(content), "Upload should be imported from lucide-react");

  // Edge case: other icons still imported
  const icons = ['ShieldAlert', 'Search', 'Bell', 'Cpu', 'AlertTriangle', 'Activity', 'Download', 'Terminal', 'Network', 'Shield', 'Mic'];
  for (const icon of icons) {
    assert.ok(content.includes(icon), `${icon} should be imported`);
  }

  // Failure case: missing Upload import should cause test to fail
  // Create a temporary copy with Upload removed from import
  const modified = originalContent.replace(
    /import\s*{[\s\S]*?Upload[\s\S]*?}\s+from\s+['"]lucide-react['"];/,
    (match) => {
      // Remove Upload from the imported list
      let modifiedImport = match.replace(/,?\s*Upload\s*,?/g, '');
      // Clean up double spaces and trailing commas before }
      modifiedImport = modifiedImport.replace(/\s+,/g, ',');
      modifiedImport = modifiedImport.replace(/,\s*}/g, '}');
      return modifiedImport;
    }
  );

  const tempPath = resolve(__dirname, '..', 'App.temp.tsx');
  writeFileSync(tempPath, modified, 'utf-8');

  const tempContent = readFileSync(tempPath, 'utf-8');
  // Assert that Upload is NOT imported
  const importPatternStill = /import\s*{[\s\S]*?Upload[\s\S]*?}\s+from\s+['"]lucide-react['"];/;
  assert.ok(!importPatternStill.test(tempContent), "Upload should NOT be imported in modified copy");
  // Assert that the usage of Upload still exists (should cause runtime error)
  assert.ok(tempContent.includes('<Upload size={24} color="#00E5FF" />'), "Usage of Upload should still be present");

  // Clean up
  unlinkSync(tempPath);

  console.log('All tests passed!');
} catch (err) {
  // If any assertion fails, we want to capture the error and write to test-results.md
  console.error('Test failed:', err);
  // Re-throw to exit with non-zero
  throw err;
}