"""
src/cache.py - Caching playlist names for verbose purpose.

Copyright (C) 2022  Harsh Sharma  <goharsh007@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

import os
import json
from utils import ensure_folder, ensure_sync_file


CACHE_FILE = os.path.expanduser("~/.cache/ypsync")
ensure_folder(CACHE_FILE)


def cache_playlist(name: str, play_id: str):
    path = os.path.join(CACHE_FILE, "playlists.json")
    ensure_sync_file(path)
    
    with open(path, "r+") as f:
        obj = json.load(f)
        print(obj)
        obj[play_id] = name
        f.truncate(0)
        f.seek(0)
        json.dump(obj, f)
        
