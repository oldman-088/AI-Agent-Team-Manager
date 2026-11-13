"""Check the Phase 0 documentation inventory without external dependencies."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = (
    'README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'CHANGELOG.md',
    'docs/RESEARCH.md', 'docs/ARCHITECTURE.md', 'docs/TECHNICAL_DECISIONS.md',
    'docs/THIRD_PARTY_DEPENDENCIES.md', 'docs/LICENSE_COMPLIANCE.md', 'docs/ROADMAP.md',
)
missing = [name for name in REQUIRED if not (ROOT / name).is_file() or not (ROOT / name).read_text(encoding='utf-8').strip()]
if missing:
    raise SystemExit('Missing or empty documentation: ' + ', '.join(missing))
print(f'Documentation inventory: {len(REQUIRED)} files present and nonempty')
