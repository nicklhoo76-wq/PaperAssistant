from typing import List, Optional, Any
from langchain_core.language_models.llms import BaseLLM as LLM
from langchain_core.outputs import LLMResult, Generation
import os
import requests

class DeepSeekLLM(LLM):
    model_name: str = "deepseek-chat"
    api_key: str = os.getenv("DEEPSEEK_API_KEY")

    @property
    def _llm_type(self) -> str:
        return "deepseek"

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> LLMResult:

        generations = []

        for prompt in prompts:
            text = self.call_deepseek(prompt)
            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)

    def call_deepseek(self, prompt: str) -> str:

        url = "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)

            print("STATUS:", resp.status_code)
            print("RESPONSE:", resp.text)

            if resp.status_code != 200:
                return f"API错误: {resp.text}"

            data = resp.json()

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            return f"请求异常: {str(e)}"