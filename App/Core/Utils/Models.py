import os
from importlib import import_module
from typing import Dict, Type

from App.Core.DB import Model
from config import DB_MODELS_NAMESPACES, ROOT


class Models:
    @staticmethod
    def load_models() -> Dict[str, Type[Model]]:
        models: Dict[str, Type[Model]] = {}

        for namespace in DB_MODELS_NAMESPACES:
            files = os.listdir(str(os.path.join(ROOT, namespace.replace('.', os.path.sep))))

            for model in files:
                if not model.endswith('.py'):
                    continue

                model = model[:-3]

                model_namespace = f"{namespace}.{model}"

                models.update({f"{model_namespace}.{model}": import_module(model_namespace).__getattribute__(model)})

        return models
