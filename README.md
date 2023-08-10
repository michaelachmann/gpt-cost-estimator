# 🚀 CostEstimator for OpenAI with tqdm integration 💸

The `CostEstimator` class offers a convenient way to estimate the cost of using OpenAI's gpt-3.5 and gpt-4 models. It is intended to be used in a loop with `tqdm` to  track and display the cost estimation in real-time.

## 🌟 Features:

![Screenshot of an estimation](images/screenshot.png)

- **tqdm Integration**: Seamlessly integrates into `tqdm` powered loops and displays the cost of each API call and the accumulated total cost.
- **Model Synonyms**: Easily switch between model versions or names. 🔄
- **Mock Responses**: Generate fake 🤖 API responses to estimate costs without making actual API requests.
- **Cost Breakdown**: Display the estimated 💰 cost per request and the accumulated cost.


## 🛠 Usage:
The CostEstimator class was designed to be used in Jupyter Notebooks, see the [example notebook](examples/example-notebook.ipynb) for a demonstration. 

1. **Initialization**:
    ```python
    from cost_estimator import CostEstimator
    estimator = CostEstimator()
    ```

2. **Decorate your API call function**:
   ```python
    @estimator()
    def call_openai_api(model="gpt-3.5-turbo-0613", temperature=0.0, messages=[...], mock=True):
    # Your API call logic here
    return openai.ChatCompletion.create(
                  model=model,
                  temperature=temperature,
                  messages=messages,
    )
    return response
    ```

3. **Call the API from within a loop**:
    ```python
    for message in tqdm(messages):
        response = call_openai_api(messages=[message], mock=False)
   
        # Or if you're mocking the API call:
        response = call_openai_api(messages=[message], mock=True)     
   
    print() # We need to print a newline to show the total cost
    ```

4. **Reset Total Cost**:
    ```python
    CostEstimator.reset()
    ```

5. **Read Total Cost**:
    ```python
    CostEstimator.get_total_cost()
    ```

## 📌 Dependencies:

- `tiktoken`: Used to determine the number of tokens in a string without making an API call.
- `openai`: Official OpenAI Python client.
- `tqdm`: Provides the real-time progress bar that displays the cost details. Essential for user-friendly cost tracking.
- `lorem_text`: Generates mock API responses.

## 🔧 Installation:

Install the necessary packages:

```bash
pip install tiktoken openai tqdm lorem_text
```
Clone this repository and import the `CostEstimator` in your script.

**pip package coming soon!** 📦

## How tqdm is Integrated:

The progress bar powered by `tqdm` provides instant feedback for every API call. Whether you're mocking the call or connecting to the real API, you'll see the cost of the current request and the total expenditure so far. It offers a visual and user-friendly way to monitor costs.

## 📝 Notes:

- Ensure the pricing details in the estimator match OpenAI's official pricing.
- Always test the estimator with your specific use cases to ensure accuracy.
- The progress bar will appear in your Jupyter notebook or console where the script runs.

## 📜 License:

The MIT License is a permissive open-source license. It allows for reuse of code with minimal restrictions, while requiring only attribution and inclusion of the original license. 🔄🔓💼