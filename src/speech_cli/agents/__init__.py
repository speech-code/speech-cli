import importlib
import logging
import pkgutil

from .base import AgentsGraph

logger = logging.getLogger(__name__)


def _build_all_agents() -> None:
    """Discover and import all agents, so they can be built.

    An agent filename must ends with '_agent.py', in order to be discovered and
    imported.
    """
    package_name = __name__
    package_path = __path__

    for _finder, mod_name, _is_pkg in pkgutil.iter_modules(package_path):
        if mod_name == "base" or not mod_name.endswith("_agent"):
            continue

        full_mod_name = f"{package_name}.{mod_name}"
        logger.debug("Importing agent: %s", full_mod_name)
        importlib.import_module(full_mod_name)


_build_all_agents()

__all__ = ["AgentsGraph"]
