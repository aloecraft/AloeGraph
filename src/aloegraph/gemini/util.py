from aloegraph.model.response_model import BaseAloeAgentResponse

from google import genai

from pydantic import BaseModel, Field
from typing import List, Type, Dict, Any, Union
import json

def generate_json_response(
    client: genai.Client,
    prompt: str,
    system_instruction: str,
    output_schema: Union[Type[BaseModel], List[Type[BaseModel]]],
    model_type="gemini-2.5-flash"
) -> Dict[str, Any]:

    # Extract schema as list or individual object
    if getattr(output_schema, "__origin__", None) is list:
        schema_dict = {
            "type": "array",
            "items": output_schema.__args__[0].model_json_schema()
        }
    else:
        schema_dict = output_schema.model_json_schema()
    try:
        # Call model to generate response
        response = client.models.generate_content(
            model=model_type,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
              temperature=0.2,
              response_mime_type="application/json",
              response_schema=schema_dict,
              system_instruction=system_instruction,
              tools=[],
          )
        )
        # Parse JSON
        try:
            return json.loads(response.text)
        except Exception:
            error = BaseAloeAgentResponse(
                success=False,
                agent_message="⚠️ Sorry, I wasn’t able to generate a response this time. Please try again.",
                error_message=f"--- 🚨 JSON Parse Error ---\n{response.text}\n\nschema_dict:\n{schema_dict}"
            )
            return error.model_dump()

    except Exception as e:
        error = BaseAloeAgentResponse(
            success=False,
            agent_message="⚠️ Sorry, I wasn’t able to generate a response this time. Please try again.",
            error_message=f"--- 🚨 LLM Generation Error ---\n{str(e)}\n\nschema_dict:\n{schema_dict}\n\n{traceback.format_exc()}"
        )
        return error.model_dump()