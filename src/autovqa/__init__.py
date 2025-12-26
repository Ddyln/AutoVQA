import importlib

from .version import __version__

__all__ = [
    "__version__",
    "eda_pipeline",
    "filter_pipeline",
    "balancer_pipeline",
]


def _get_attr(module_name: str, attr: str):
    mod = importlib.import_module(module_name)
    return getattr(mod, attr)


def eda_pipeline(*args, **kwargs):
    return _get_attr("autovqa.eda.eda_pipeline", "eda_pipeline")(*args, **kwargs)


def filter_pipeline(*args, **kwargs):
    return _get_attr("autovqa.filter.filter_pipeline", "filter_pipeline")(
        *args, **kwargs
    )


def balancer_pipeline(*args, **kwargs):
    return _get_attr("autovqa.balancer.balancer_pipeline", "balancer_pipeline")(
        *args, **kwargs
    )
