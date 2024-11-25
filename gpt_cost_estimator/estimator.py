from tqdm.notebook import tqdm
import functools
from lorem_text import lorem
from .utils import num_tokens_from_messages


class CostEstimator:
    MODEL_SYNONYMS = {
    }

    # Source: https://openai.com/pricing
    # Prices in $ per 1000 tokens
    # Last updated: 2024-11-25
    DEFAULT_PRICES = {
        # GPT 3.5 Models
        "gpt-3.5-turbo": {"input": 0.003, "output": 0.006},
        "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002},
        "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002},
        "gpt-3.5-turbo-16k-0613": {"input": 0.003, "output": 0.004},
        "gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002},
        # GPT 4 Models
        "gpt-4-0613": {"input": 0.03, "output": 0.06},
        "gpt-4-0125-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-2024-04-09": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-32k": {"input": 0.06, "output": 0.12},
        # GPT-4o Pricing
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4o-mini-2024-07-18": {"input": 0.00015, "output": 0.0006},
        "gpt-4o-2024-11-20": {"input": 0.0025, "output": 0.01},
        "gpt-4o-2024-08-06": {"input": 0.0025, "output": 0.01},
        "gpt-4o-audio-preview": {"input": 0.25, "output": 2.00},  # Audio mode pricing
        "gpt-4o-realtime-preview": {"input": 0.005, "output": 0.02},
        # O1 Models
        "o1-preview": {"input": 0.015, "output": 0.06},
        "o1-preview-2024-09-12": {"input": 0.015, "output": 0.06},
        "o1-mini": {"input": 0.003, "output": 0.012},
        "o1-mini-2024-09-12": {"input": 0.003, "output": 0.012},
        # Embedding Models
        "text-embedding-3-small": {"input": 0.00002, "output": 0.00002},
        "text-embedding-3-large": {"input": 0.00013, "output": 0.00013},
        "ada-v2": {"input": 0.0001, "output": 0.0001},
        # Whisper and TTS
        "whisper": {"input": 0.006, "output": 0.006},
        "tts": {"input": 0.015, "output": 0.015},
        "tts-hd": {"input": 0.03, "output": 0.03},
    }

    total_cost = 0.0  # class variable to persist total_cost

    def __init__(self, price_overrides=None) -> None:
        """
        Initialize the CostEstimator class.

        :param price_overrides: Optional dictionary to override default prices.
        """
        self.default_model = "gpt-4o-mini"
        # Apply price overrides if provided
        self.PRICES = {**self.DEFAULT_PRICES, **(price_overrides or {})}


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
