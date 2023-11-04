import inspect
from slither_core import Slither
from slither_core.detectors import all_detectors
from slither_core.detectors.abstract_detector import AbstractDetector


def _run_all_detectors(slither: Slither) -> None:
    detectors = [getattr(all_detectors, name) for name in dir(all_detectors)]
    detectors = [d for d in detectors if inspect.isclass(d) and issubclass(d, AbstractDetector)]

    for detector in detectors:
        slither.register_detector(detector)

    slither.run_detectors()
