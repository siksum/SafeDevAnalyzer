from pathlib import Path
import os

class Filename: #원래 used, short가 있었는데 왜 필요한지 모르겠어서 절대/상대 경로만 우선 넣어둠
    def __init__(self, absolute: str, relative: str):
        self.absolute = absolute
        self.relative = relative
    
    def __hash__(self) -> int:
        return hash(self.relative)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Filename):
            return NotImplemented
        return self.relative == other.relative

    def __repr__(self) -> str:
        return f"Filename(absolute={self.absolute}, relative={self.relative}))"

def convert_filename(filename: str, working_dir: Path):
    if isinstance(filename, Filename):
        return filename

    filename = Path(filename)
    absolute = Path(os.path.abspath(filename))
    try:
        relative = Path(os.path.relpath(filename, Path.cwd()))
    except ValueError:
        relative = Path(filename)


    return Filename(absolute=str(absolute), relative=relative.as_posix())