"""Run only in a new Blender file: blender -b --factory-startup --python scripts/rebuild.py."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
import farm_scene as farm
farm.setup()
farm.landscape()
farm.plants()
farm.details()
farm.configure('desktop')
farm.export()
import journey_scene as journey
journey.build()
journey.configure('mobile')
journey.configure('desktop')
journey.export()
