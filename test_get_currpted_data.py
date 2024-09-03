from pathlib import Path
import matplotlib.pyplot as plt
from allensdk.brain_observatory.behavior.behavior_project_cache import VisualBehaviorNeuropixelsProjectCache
from urllib.parse import urljoin

drive_dir = "/Volumes/Brain2024/project"
output_dir =  drive_dir
output_dir = Path(output_dir)

cache = VisualBehaviorNeuropixelsProjectCache.from_s3_cache(cache_dir=output_dir)

behavior_sessions = cache.get_behavior_session_table()

sub_sessions = [1061722976]

print('Num wt mouse sessions:', len(sub_sessions))

# Download behavior only mouse:
i = 1
for bsid in  sub_sessions:
    print(f'\n Downlading {i}th Session with bsid:', bsid)
    _ = cache.get_behavior_session(behavior_session_id=bsid)
    i += 1