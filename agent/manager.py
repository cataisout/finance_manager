import json 
import os
from openai import OpenAI
from openai import RateLimitError
import time


class Agent():
    
    def __init__(self, instructions: str) -> None:

        self.client =  OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.getenv("HF_TOKEN")
        )

        self.instructions = instructions

        pass

    
    def _build_prompt(self, instruction: str | None = None, schema: dict | None = None) -> str:

        parts = [self.instructions]

        if instruction:
            parts.append(instruction)

        if schema:
            parts.append(f"""
            Você deve retornar um schema valido seguindo esse exemplo:
                {json.dumps(schema, indent=2)}

                Sem explicações ou textos extras
                """)

        return "\n\n".join(parts).strip()
    
    def invoke(self, user_input, extra_instruction : str | None = None) -> str:

        instruction = self.instructions

        if extra_instruction:
            instruction = self._build_prompt(instruction = extra_instruction )
        tries = 3
        while tries > 0:
            try:
                response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b:cerebras",
                messages=[{"role": "system", "content": instruction}, {"role": "user", "content": user_input}],
                )

                if response: break
            except RateLimitError:
                print("RateLimitError Detected while generating response. Waiting 10 seconds before trying again")
                time.sleep(10)
                tries-=1

        return str(response.choices[0].message.content)
    
    def structured_invoke(self, user_input: str, schema: dict, max_retries: int = 3) -> dict:

    
        for attempt in range(max_retries):

            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b:cerebras",
                messages=[
                    {"role": "system", "content": self._build_prompt(schema=schema)},
                    {"role": "user", "content": user_input}
                ],
                # tenta usar enforcement nativo se existir
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "structured_output",
                        "schema": schema
                    }
                }
            )

            content = response.choices[0].message.content

            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                continue

        raise ValueError("LLM failed to return valid structured output after retries")

