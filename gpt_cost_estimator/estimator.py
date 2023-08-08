from tqdm.notebook import tqdm
import functools
from lorem_text import lorem
from .utils import num_tokens_from_messages


class CostEstimator:
    MODEL_SYNONYMS = {
        "gpt-4": "gpt-4-0613",
        "gpt-3": "gpt-3.5-turbo-0613",
    }

    PRICES = {
        "gpt-4-0613": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002},
    }

    total_cost = 0  # class variable to persist total_cost

    def __init__(self, mock_token_length: int = 1) -> None:
        self.mock_token_length = mock_token_length

    @classmethod
    def reset(cls) -> None:
        cls.total_cost = 0

    def __call__(self, function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            mock = kwargs.get('mock', True)
            model = kwargs.get('model', self.model)
            model = self.MODEL_SYNONYMS.get(model, model)

            messages = kwargs.get("messages")
            input_tokens = num_tokens_from_messages(messages, model)

            if mock:
                mock_content = lorem.words(self.mock_token_length) or "Default response"
                output_tokens = num_tokens_from_messages([{"role": "assistant", "content": mock_content}], model)
            else:
                response = function(*args, **kwargs)
                output_tokens = response["usage"]["total_tokens"] - input_tokens

            # Calculate cost
            total_tokens = input_tokens + output_tokens
            cost = (self.PRICES[model]['input'] * input_tokens + self.PRICES[model]['output'] * output_tokens) / 1000
            CostEstimator.total_cost += cost

            # Display progress bar and cost with tqdm
            tqdm.write(f"Cost: ${cost:.4f} | Total: ${CostEstimator.total_cost:.4f}", end='\r')

            if mock:
                return {'choices': [{'message': {'content': mock_content}}]}
            return response

        return wrapper
