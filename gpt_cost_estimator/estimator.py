from tqdm.notebook import tqdm
import functools
from lorem_text import lorem
from .utils import num_tokens_from_messages


class CostEstimator:
    MODEL_SYNONYMS = {
        "gpt-4": "gpt-4-0613",
        "gpt-3-turbo": "gpt-3.5-turbo-0613",
    }

    # Source: https://openai.com/pricing
    # Prices in $ per 1000 tokens
    # Last updated: 2023-08-10
    PRICES = {
        "gpt-4-0613": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002},
    }

    total_cost = 0.0  # class variable to persist total_cost

    def __init__(self) -> None:
        self.default_model = "gpt-3.5-turbo-0613"

    @classmethod
    def reset(cls) -> None:
        cls.total_cost = 0.0

    def get_total_cost(self) -> float:
        return CostEstimator.total_cost

    def __call__(self, function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            mock = kwargs.get('mock', True)
            model = kwargs.get('model', self.default_model)
            model = self.MODEL_SYNONYMS.get(model, model)
            completion_tokens = kwargs.get('completion_tokens', 1)

            messages = kwargs.get("messages")
            input_tokens = num_tokens_from_messages(messages, model=model)

            if mock:
                mock_output_message_content = lorem.words(completion_tokens) if completion_tokens else "Default response"
                mock_output_messages = {
                    'choices': [
                        {
                            'message': {
                                'content': mock_output_message_content
                            }
                        }
                    ]
                }
                output_tokens = num_tokens_from_messages([{"role": "assistant", "content": mock_output_message_content}], model=model)
                total_tokens = input_tokens + output_tokens
            else:
                response = function(*args, **kwargs)
                total_tokens = response.usage.total_tokens
                output_tokens = total_tokens - input_tokens

            input_cost = input_tokens * self.PRICES[model]['input'] / 1000
            output_cost = output_tokens * self.PRICES[model]['output'] / 1000
            cost = input_cost + output_cost
            CostEstimator.total_cost += cost  # update class variable


            # Display progress bar and cost with tqdm
            tqdm.write(f"Cost: ${cost:.4f} | Total: ${CostEstimator.total_cost:.4f}", end='\r')
            return mock_output_messages if mock else response
        return wrapper
