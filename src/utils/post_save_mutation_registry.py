from typing import Dict, List, Callable, Any
from utils.logging import logger


class PostSaveMutationRegistry:
    post_save_methods: Dict[str, Any] = dict()

    @classmethod
    def register_post_save_method(
        cls, function: Callable[..., Any], model_name: str
    ) -> None:
        model_name = model_name.lower()
        if not callable(function):  # type: ignore
            raise ValueError("Function must be a callable")

        if not isinstance(model_name, str):  # type: ignore
            raise ValueError("Model name needs to be a 'str'")

        cls.post_save_methods[model_name] = cls.post_save_methods.get(
            model_name, set()
        ).union({function})
        # logger.info(
        #     # f"Registered Post_Save Method '{function.__name__}' on '{model_name.capitalize()}' model"
        # )

    @classmethod
    def get_post_save_methods(cls, model_name: str) -> List[Callable[..., Any]] | List:
        model_name = model_name.lower()
        handlers = cls.post_save_methods.get(model_name, [])
        return list(handlers)
