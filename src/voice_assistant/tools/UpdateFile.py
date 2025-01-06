import json
import os

from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.models import FileSelectionResponse, ModelName
from voice_assistant.utils.decorators import timeit_decorator
from voice_assistant.utils.llm_utils import (
    get_structured_output_completion,
    parse_chat_completion,
)

load_dotenv()


class UpdateFile(BaseTool):
    """A tool for updating the content of a file based on a prompt."""

    prompt: str = Field(
        ...,
        description="The prompt to identify which file to update and how to update it.",
    )

    async def run(self):
        result = await update_file(self.prompt)
        if "model_used" in result and isinstance(result["model_used"], ModelName):
            result["model_used"] = result["model_used"].value
        return str(result)


@timeit_decorator
async def update_file(prompt: str) -> dict:
    available_files = os.listdir(SCRATCH_PAD_DIR)
    available_model_map = {model.value: model.name for model in ModelName}

    file_selection_response = await get_structured_output_completion(
        create_file_selection_prompt(
            available_files, json.dumps(available_model_map), prompt
        ),
        FileSelectionResponse,
    )

    if not file_selection_response.file:
        return {"status": "No matching file found"}

    selected_file = file_selection_response.file
    selected_model = file_selection_response.model or ModelName.BASE_MODEL
    file_path = os.path.join(SCRATCH_PAD_DIR, selected_file)

    with open(file_path, "r") as f:
        file_content = f.read()

    updated_content = await parse_chat_completion(
        create_file_update_prompt(selected_file, file_content, prompt),
        selected_model,
    )

    with open(file_path, "w") as f:
        f.write(updated_content)

    return {
        "status": "File updated",
        "file_name": selected_file,
        "model_used": selected_model,
    }


def create_file_selection_prompt(available_files, available_model_map, user_prompt):
    return f"""
<purpose>
    Select a file from the available files and choose the appropriate model based on the user's prompt.
</purpose>

<instructions>
    <instruction>Based on the user's prompt and the list of available files, infer which file the user wants to update.</instruction>
    <instruction>Also, select the most appropriate model from the available models mapping.</instruction>
    <instruction>If the user does not specify a model, default to 'base_model'.</instruction>
    <instruction>If no file matches, return an empty string for 'file'.</instruction>
</instructions>

<available-files>
    {", ".join(available_files)}
</available-files>

<available-model-map>
    {available_model_map}
</available-model-map>

<user-prompt>
    {user_prompt}
</user-prompt>
    """


def create_file_update_prompt(file_name, file_content, user_prompt):
    return f"""
<purpose>
    Update the content of the file based on the user's prompt.
</purpose>

<instructions>
    <instruction>Based on the user's prompt and the file content, generate the updated content for the file.</instruction>
    <instruction>The file-name is the name of the file to update.</instruction>
    <instruction>The user's prompt describes the updates to make.</instruction>
    <instruction>Respond exclusively with the updates to the file and nothing else; they will be used to overwrite the file entirely using f.write().</instruction>
    <instruction>Do not include any preamble or commentary or markdown formatting, just the raw updates.</instruction>
    <instruction>Be precise and accurate.</instruction>
</instructions>

<file-name>
    {file_name}
</file-name>

<file-content>
    {file_content}
</file-content>

<user-prompt>
    {user_prompt}
</user-prompt>
    """


if __name__ == "__main__":
    import asyncio

    tool = UpdateFile(prompt="Update the test file to include a paragraph about AI")
    print(asyncio.run(tool.run()))
