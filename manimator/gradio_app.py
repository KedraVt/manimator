import gradio as gr
import re
from importlib import resources
from typing import Tuple, Optional, Dict
import functools

from manimator.api.animation_generation import generate_animation_response
from manimator.api.scene_description import process_prompt_scene, process_pdf_prompt
from manimator.utils.schema import ManimProcessor


def process_prompt(prompt: str):
    max_attempts = 2
    attempts = 0

    while attempts < max_attempts:
        try:
            processor = ManimProcessor()
            with processor.create_temp_dir() as temp_dir:
                scene_description = process_prompt_scene(prompt)
                response = generate_animation_response(scene_description)
                code = processor.extract_code(response)

                if not code:
                    attempts += 1
                    if attempts < max_attempts:
                        continue
                    return (
                        None,
                        None,
                        "No valid Manim code generated after multiple attempts",
                    )

                class_match = re.search(r"class (\w+)\(Scene\)", code)
                if not class_match:
                    attempts += 1
                    if attempts < max_attempts:
                        continue
                    return None, None, "No Scene class found after multiple attempts"

                scene_name = class_match.group(1)
                scene_file = processor.save_code(code, temp_dir)
                video_path = processor.render_scene(scene_file, scene_name, temp_dir)

                if not video_path:
                    return None, None, "Failed to render animation"

                return video_path, code, "Animation generated successfully!"

        except Exception as e:
            attempts += 1
            if attempts < max_attempts:
                continue
            return None, None, f"Error after multiple attempts: {str(e)}"


def process_pdf(file_path: str):
    print("file_path", file_path)
    try:
        if not file_path:
            return "Error: No file uploaded"
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            scene_description = process_pdf_prompt(file_bytes)
            print("scene_description", scene_description)
        return scene_description
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


def interface_fn(prompt=None, pdf_file=None):
    if prompt:
        video_path, code, message = process_prompt(prompt)
        if video_path:
            return [video_path, code, message]
        return [None, None, message]
    elif pdf_file:
        scene_description = process_pdf(pdf_file)
        if scene_description:
            video_path, code, message = process_prompt(scene_description)
            if video_path:
                return [video_path, code, message]
            return [None, None, message]
    return [None, None, "Please provide either a prompt or upload a PDF file"]


description_md = """
## 🎬 manimator

This tool helps you create visualizations of complex concepts using natural
language or PDF papers:

- **Text Prompt**: Describe the concept you want to visualize
- **PDF Upload**: Upload a research paper to extract key visualizations

### Links
- [Manim Documentation](https://docs.manim.community/)
- [Project Repository](https://github.com/HyperCluster-Tech/manimator)
"""

# Constants for examples
EXAMPLE_VIDEOS: Dict[str, str] = {
    "What is a CNN?": "CNNExplanation.mp4",
    "BitNet Paper": "BitNet.mp4",
    "Explain Fourier Transform": "FourierTransformExplanation.mp4",
    "How does backpropagation work in Neural Networks?": (
        "NeuralNetworksBackPropagationExample.mp4"
    ),
    "What is SVM?": "SVMExplanation.mp4",
}


@functools.lru_cache(maxsize=None)
def get_example_path(filename: str) -> Optional[str]:
    """Get absolute path to example file using importlib.resources."""
    try:
        with resources.path("manimator.examples", filename) as path:
            if path.exists():
                return str(path)
    except Exception as e:
        print(f"Error loading example {filename}: {e}")
    return None


def show_sample(example: str) -> Tuple[Optional[str], str]:
    """Display sample animation with proper path resolution."""
    if example not in EXAMPLE_VIDEOS:
        return None, "Invalid example selected"

    video_path = get_example_path(EXAMPLE_VIDEOS[example])
    if not video_path:
        return None, f"Example file {EXAMPLE_VIDEOS[example]} not found"

    return video_path, f"Showing example: {example}"


with gr.Blocks(title="manimator") as demo:
    gr.Markdown(description_md)

    with gr.Tabs():
        with gr.TabItem("✍️ Text Prompt"):
            with gr.Column():
                text_input = gr.Textbox(
                    label="Describe the animation you want to create",
                    placeholder="Explain the working of neural networks",
                    lines=3,
                )
                text_button = gr.Button("Generate Animation from Text")

            with gr.Row():
                video_output = gr.Video(label="Generated Animation")

            code_output = gr.Code(
                label="Generated Manim Code",
                language="python",
                interactive=False,
            )
            status_output = gr.Textbox(
                label="Status", interactive=False, show_copy_button=True
            )
            text_button.click(
                fn=interface_fn,
                inputs=[text_input],
                outputs=[video_output, code_output, status_output],
            )

        with gr.TabItem("📄 PDF Upload"):
            with gr.Column():
                file_input = gr.File(label="Upload a PDF paper", file_types=[".pdf"])
                pdf_button = gr.Button("Generate Animation from PDF")

            with gr.Row():
                pdf_video_output = gr.Video(label="Generated Animation")

            pdf_code_output = gr.Code(
                label="Generated Manim Code",
                language="python",
                interactive=False,
            )
            pdf_status_output = gr.Textbox(
                label="Status", interactive=False, show_copy_button=True
            )
            pdf_button.click(
                fn=lambda pdf: interface_fn(prompt=None, pdf_file=pdf),
                inputs=[file_input],
                outputs=[pdf_video_output, pdf_code_output, pdf_status_output],
            )

        with gr.TabItem("Sample Examples"):
            sample_select = gr.Dropdown(
                choices=list(EXAMPLE_VIDEOS.keys()),
                label="Choose an example to display",
                value=None,
            )
            sample_video = gr.Video()
            sample_markdown = gr.Markdown()

            sample_select.change(
                fn=show_sample,
                inputs=sample_select,
                outputs=[sample_video, sample_markdown],
            )


def main():
    """Entry point for the Manimator application."""
    demo.launch()


if __name__ == "__main__":
    main()
