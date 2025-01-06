import os

from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.models import FileDeleteResponse
from voice_assistant.utils.decorators import timeit_decorator
from voice_assistant.utils.llm_utils import get_structured_output_completion

load_dotenv()


class DeleteFile(BaseTool):
    """A tool for deleting a file based on a prompt."""

    prompt: str = Field(..., description="The prompt to identify which file to delete.")
    force_delete: bool = Field(
        False, description="Whether to force delete the file without confirmation."
    )

    async def run(self):
        result = await delete_file(self.prompt, self.force_delete)
        return str(result)


@timeit_decorator
async def delete_file(prompt: str, force_delete: bool = False) -> dict:
    available_files = os.listdir(SCRATCH_PAD_DIR)

    # Select file to delete based on user prompt
    file_delete_response = await get_structured_output_completion(
        create_file_selection_prompt(available_files, prompt), FileDeleteResponse
    )

    if not file_delete_response.file:
        return {"status": "No matching file found"}

    file_path = os.path.join(SCRATCH_PAD_DIR, file_delete_response.file)

    if not os.path.exists(file_path):
        return {"status": "File does not exist", "file_name": file_delete_response.file}

    if not force_delete:
        return {
            "status": "Confirmation required",
            "file_name": file_delete_response.file,
            "message": f"Are you sure you want to delete '{file_delete_response.file}'? Say force delete if you want to delete.",
        }

    os.remove(file_path)
    return {"status": "File deleted", "file_name": file_delete_response.file}


def create_file_selection_prompt(available_files, user_prompt):
    return f"""
<purpose>
    Select a file from the available files to delete.
</purpose>

<instructions>
    <instruction>Based on the user's prompt and the list of available files, infer which file the user wants to delete.</instruction>
    <instruction>If no file matches, return an empty string for 'file'.</instruction>
</instructions>

<available-files>
    {", ".join(available_files)}
</available-files>

<user-prompt>
    {user_prompt}
</user-prompt>
    """


if __name__ == "__main__":
    import asyncio

    tool = DeleteFile(prompt="Delete the test file", force_delete=True)
    print(asyncio.run(tool.run()))
