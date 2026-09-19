from typing import Dict, List, Any

# Centralized In-Memory Database Repositories
plans_db: Dict[str, Dict[str, Any]] = {}
stories_db: Dict[str, Dict[str, Any]] = {}
storyboards_db: Dict[str, Dict[str, Any]] = {}
characters_db: Dict[str, List[Any]] = {}
images_db: Dict[str, List[Any]] = {}
animations_db: Dict[str, List[Any]] = {}
audios_db: Dict[str, List[Any]] = {}
music_mixes_db: Dict[str, List[Any]] = {}
timelines_db: Dict[str, Any] = {}
renders_db: Dict[str, List[Any]] = {}
publishing_db: Dict[str, Dict[str, Any]] = {}
