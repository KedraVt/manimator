import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from typing import Optional
from fastapi import HTTPException


class ManimProcessor:
    """Handles Manim animation processing, including code extraction and video
    rendering.

    This class provides utilities for:
    - Creating temporary directories for processing
    - Extracting Python code from model response
    - Saving and rendering Manim scenes
    """

    @contextmanager
    def create_temp_dir(self):
        """Creates and manages a temporary directory for processing Manim files.

        Yields:
            str: Path to the temporary directory

        Note:
            Automatically cleans up directory and contents when context exits
        """

        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(temp_dir)

    def extract_code(self, response: str) -> Optional[str]:
        """Extracts Python code blocks from the model's response.

        Args:
            response (str): Response string containing code blocks

        Returns:
            Optional[str]: Extracted Python code if found, None otherwise
        """

        pattern = r"```python\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        return match.group(1).strip() if match else None

    def save_code(self, code: str, temp_dir: str) -> str:
        """Saves Manim code to a temporary Python file.

        Args:
            code (str): Python code to save
            temp_dir (str): Directory to save the file in

        Returns:
            str: Path to the saved Python file
        """

        scene_file = os.path.join(temp_dir, "scene.py")
        with open(scene_file, "w") as f:
            f.write("from manim import *\n\n")
            f.write(code)
        return scene_file

    def render_scene(
        self, scene_file: str, scene_name: str, temp_dir: str
    ) -> Optional[str]:
        """Renders a Manim scene to video.

        Args:
            scene_file (str): Path to the Python file containing the scene
            scene_name (str): Name of the scene class to render
            temp_dir (str): Directory for output media files

        Returns:
            Optional[str]: Path to rendered video file if successful, None otherwise

        Raises:
            HTTPException: If rendering fails with status code 500
        """

        cmd = [
            "manim",
            "-pql",
            "--media_dir",
            temp_dir,
            scene_file,
            scene_name,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            video_path = os.path.join(
                temp_dir, "videos", "scene", "480p15", f"{scene_name}.mp4"
            )

            if not os.path.exists(video_path):
                return None

            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            with open(video_path, "rb") as f:
                temp_video.write(f.read())
            return temp_video.name

        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Render error: {e.stderr}")
