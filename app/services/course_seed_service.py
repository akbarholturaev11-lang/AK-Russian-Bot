import importlib.util
from pathlib import Path

from sqlalchemy import func, select

from app.db.models.course_lessons import CourseLesson


class CourseSeedService:
    def __init__(self, session):
        self.session = session

    async def count_lessons(self) -> int:
        count = await self.session.scalar(
            select(func.count()).select_from(CourseLesson)
        )
        return int(count or 0)

    async def sync_all_lessons(self) -> int:
        for seed_path in self._iter_seed_paths():
            seed_callable = self._load_seed_callable(seed_path)
            await seed_callable()
        return await self.count_lessons()

    def _iter_seed_paths(self) -> list[Path]:
        scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
        seed_paths = sorted(scripts_dir.glob("seed_hsk1_lesson_*.py"))

        combined_hsk2 = scripts_dir / "seed_hsk2_lessons_1_8.py"
        if combined_hsk2.exists():
            seed_paths.append(combined_hsk2)

        seed_paths.extend(sorted(scripts_dir.glob("seed_hsk2_lesson_*.py")))
        seed_paths.extend(sorted(scripts_dir.glob("seed_hsk3_lesson_*.py")))
        seed_paths.extend(sorted(scripts_dir.glob("seed_hsk4_lesson_*.py")))
        return seed_paths

    def _load_seed_callable(self, seed_path: Path):
        module_name = f"_course_seed_{seed_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, seed_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load seed module: {seed_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for attr in ("seed", "upsert_lesson", "upsert_lessons"):
            seed_callable = getattr(module, attr, None)
            if seed_callable is not None:
                return seed_callable

        raise RuntimeError(f"No seed entrypoint found in {seed_path.name}")
