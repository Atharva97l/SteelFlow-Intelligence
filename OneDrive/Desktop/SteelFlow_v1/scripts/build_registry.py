from pathlib import Path
import json

ROOT = Path(__file__).parents[1]
model_dir = ROOT / 'artifacts' / 'models'
registry = []
for path in sorted(model_dir.glob('*.joblib')):
    registry.append({'artifact': path.name, 'task': path.stem.replace('_best', ''), 'status': 'trained_pipeline'})
(model_dir / 'registry.json').write_text(json.dumps(registry, indent=2), encoding='utf-8')
print(f'Registered {len(registry)} pipelines')
