# src/aloegraph/V2/response_generator.py
"""
response_generator
==========================

- **Module:** `src/aloegraph/V2/response_generator.py`
- **GitHub:** <https://github.com/aloecraft/AloeGraph>
- **Author:** AloeCraft.org (Michael Godfrey)

Defines abstract and concrete classes for generating structured JSON responses
from large language models (LLMs) in AloeGraph V2.

Overview
--------
- **JSONResponseGeneratorBase**:
  An abstract generic base class parameterized by a `BaseResponse` type.
  Provides the contract for generating agent responses as validated Pydantic
  models. It manages:
    * Generic type resolution (`response_T`)
    * Schema extraction (`schema_dict`)
    * System instruction construction (`system_instruction`)
    * Subclass initialization hooks

- **GeminiJSONResponseGenerator**:
  Concrete implementation of `JSONResponseGeneratorBase` that integrates with
  Google's Gemini API. It sends prompts to the model, requests JSON output
  conforming to the response schema, and validates the result against the
  specified `BaseResponse` type. Errors in generation or parsing are caught
  and returned as structured failure responses.

Key Concepts
------------
- **BaseResponse**:
  All response types must inherit from `BaseResponse`, ensuring a consistent
  schema with `success`, `agent_message`, and `error_message` fields.

- **Generic parameterization**:
  `JSONResponseGeneratorBase[responseT]` enforces that subclasses specify
  the concrete response type they produce. This allows automatic schema
  extraction and validation.

- **System instructions**:
  Each response type defines a `SYSTEM_INSTRUCTION` classmethod. Generators
  use this to guide the LLM in producing structured outputs.

Usage
-----
Subclass `JSONResponseGeneratorBase` or use `GeminiJSONResponseGenerator`
directly to generate validated responses:

```python
class ChatAgentResponse(BaseResponse):
    @classmethod
    def SYSTEM_INSTRUCTION(cls, agent_name: str, agent_description: str) -> str:
        return f"{agent_name}: {agent_description}"

generator = GeminiJSONResponseGenerator[ChatAgentResponse](
    client=genai.Client(),
    agent_name="ChatAgent",
    agent_description="Handles user conversations"
)

response = generator.generate("Hello, world!")
print(response.success, response.agent_message)
```
"""

from aloegraph.V2.v2_base_response import BaseResponse

from abc import ABC, abstractmethod
import typing

class JSONResponseGeneratorBase[responseT: BaseResponse](ABC):
    """
    Abstract generic base class for JSON response generators.

    This class defines the contract for agents that generate structured
    responses from large language models. It is parameterized by a
    `BaseResponse` subclass, ensuring that all generated outputs conform
    to a validated schema.

    Responsibilities
    ----------------
    - Provide an abstract `generate` method that subclasses must implement
      to call an LLM and return a validated response.
    - Manage generic type resolution (`response_T`) to determine the
      concrete response type.
    - Expose the JSON schema (`schema_dict`) for the response type,
      used to enforce structured outputs.
    - Construct the system instruction string (`system_instruction`)
      from agent metadata, guiding the LLM in response generation.
    - Wrap subclass initialization to set up caches and metadata.

    Type Parameters
    ---------------
    responseT : BaseResponse
        The concrete response type produced by the generator.
    """
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: str = None,
        model_type="gemini-2.5-flash",
        temperature: float = 0.2
    ) -> responseT:
        """
        Abstract method for generating a structured agent response.

        Subclasses must implement this method to send a prompt to a model,
        apply system instructions, and return a validated `BaseResponse`
        instance. The implementation is responsible for ensuring that the
        returned object conforms to the schema defined by `responseT`.

        Parameters
        ----------
        prompt : str
            The user or agent prompt to send to the model.
        system_instruction : str, optional
            Instruction string guiding the model's behavior. If not provided,
            subclasses may use the default `system_instruction` property.
        model_type : str, default "gemini-2.5-flash"
            Identifier for the model backend to use.
        temperature : float, default 0.2
            Sampling temperature controlling randomness in generation.

        Returns
        -------
        responseT
            A validated response object of type `BaseResponse`.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.
        """
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        original_init = cls.__init__
        def wrapped_init(self, *args, **kwargs):
            self._response_T = None  # Create a cache
            self._schema_dict = None
            self._system_instruction = None
            if callable(original_init):
                original_init(self,*args, **kwargs)
        cls.__init__ = wrapped_init

    def __init__(self, agent_name: str, agent_description:str):
        self.agent_name = agent_name
        self.agent_description = agent_description

    @property
    def response_T(self) -> type[responseT]:
        """
        Resolve and cache the concrete response type parameter.

        This property inspects the generic type arguments of the class
        (`__orig_class__`) to determine the specific `BaseResponse` subclass
        used for this generator. The result is cached for reuse.

        Returns
        -------
        type[responseT]
            The concrete `BaseResponse` subclass specified as the generic
            parameter.

        Raises
        ------
        TypeError
            If no generic type argument was provided when subclassing.
        """        
        if getattr(self, "_response_T", None) is None:
            type_args = typing.get_args(self.__orig_class__)
            if not type_args:
                raise TypeError("ResponseType generic, 'responseT' not specified")
            self._response_T = type_args[0]
        return self._response_T
    
    @property
    def schema_dict(self) -> dict:
        """
        Lazily retrieve the JSON schema for the response type.

        Uses the `response_T` property to access the Pydantic model schema
        (`model_json_schema`) and caches the result. This schema is passed
        to the LLM to enforce structured JSON output.

        Returns
        -------
        dict
            JSON schema dictionary describing the response model.
        """
        if self._schema_dict is None:
            self._schema_dict = self.response_T.model_json_schema()
        return self._schema_dict
    
    @property
    def system_instruction(self) -> dict:
        """
        Construct and cache the system instruction string.

        Calls the `SYSTEM_INSTRUCTION` classmethod of the response type,
        passing the agent name and description. This instruction guides
        the LLM in producing responses that conform to the agent’s role.

        Returns
        -------
        str
            System instruction string for the agent.
        """        
        if self._system_instruction is None:
            self._system_instruction = self.response_T.SYSTEM_INSTRUCTION(self.agent_name, self.agent_description)
        return self._system_instruction
    

from google import genai
import traceback
class GeminiJSONResponseGenerator[responseT: BaseResponse](JSONResponseGeneratorBase[responseT]):
    """
    Concrete JSON response generator using Google's Gemini API.

    Implements the `generate` method to send prompts to the Gemini model,
    request structured JSON output conforming to the schema of the
    specified `BaseResponse` type, and validate the result. Handles
    both generation errors and JSON parsing errors gracefully by
    returning structured failure responses.

    Responsibilities
    ----------------
    - Integrate with the Gemini client to call `models.generate_content`.
    - Pass the response schema and system instruction to enforce
      structured outputs.
    - Validate the returned JSON against the `BaseResponse` schema.
    - Catch and wrap errors (generation failures, parse errors) in
      a consistent `BaseResponse` with `success=False`.

    Type Parameters
    ---------------
    responseT : BaseResponse
        The concrete response type produced by the generator.

    Example
    -------
    ```python
    generator = GeminiJSONResponseGenerator[ChatAgentResponse](
        client=genai.Client(),
        agent_name="ChatAgent",
        agent_description="Handles user conversations"
    )
    response = generator.generate("Hello, world!")
    print(response.success, response.agent_message)
    ```
    """
    def generate(
        self,
        prompt: str,
        system_instruction: str = None,
        model_type="gemini-2.5-flash",
        temperature: float = 0.2
    ) -> responseT:
        """
        Generate a structured JSON response using Google's Gemini API.

        Sends the given prompt to the Gemini model, requesting output in JSON
        format that conforms to the schema of the specified `BaseResponse`
        type. Attempts to validate the returned JSON against the schema. If
        validation fails or the API call raises an exception, returns a
        structured error response with `success=False`.

        Parameters
        ----------
        prompt : str
            The user or agent prompt to send to the Gemini model.
        system_instruction : str, optional
            Instruction string guiding the model's behavior. If not provided,
            the generator uses the default `system_instruction` property.
        model_type : str, default "gemini-2.5-flash"
            Identifier for the Gemini model to use.
        temperature : float, default 0.2
            Sampling temperature controlling randomness in generation.

        Returns
        -------
        responseT
            A validated response object of type `BaseResponse`. If generation
            or parsing fails, returns a `BaseResponse` with `success=False`
            and error details populated.

        Error Handling
        --------------
        - **JSON Parse Error**:
          Raised if the Gemini model returns invalid JSON. The generator
          wraps the error in a `BaseResponse` with `success=False` and
          includes the raw response text and schema in `error_message`.

        - **LLM Generation Error**:
          Raised if the Gemini API call fails. The generator returns a
          structured error response with traceback details in `error_message`.
        """        

        try:
            response = self.client.models.generate_content(
                model=model_type, contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                    response_schema=self.schema_dict,
                    system_instruction=system_instruction or self.system_instruction,
                    tools=[]))
            try:
                return self.response_T.model_validate_json(response.text)
            except Exception as e:
                return self.response_T(
                    success=False,
                    agent_message="⚠️ Sorry, I wasn’t able to generate a response this time. Please try again.",
                    error_message=f"--- 🚨 JSON Parse Error ---\n{response.text}\n\nschema_dict:\n{self.schema_dict}\n\nException:{e}")
        except Exception as e:
            return self.response_T(
                success=False,
                agent_message="⚠️ Sorry, I wasn’t able to generate a response this time. Please try again.",
                error_message=f"--- 🚨 LLM Generation Error ---\n{str(e)}\n\nschema_dict:\n{self.schema_dict}\n\n{traceback.format_exc()}")

    def __init__(self, client: genai.Client, agent_name: str, agent_description:str):
        self.client = client
        self.agent_name = agent_name
        self.agent_description = agent_description