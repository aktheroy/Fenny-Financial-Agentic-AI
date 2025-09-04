import os
from huggingface_hub import hf_hub_download
from pathlib import Path


def download_finance_model():
    """Download the finance-chat model to the correct location"""
    model_dir = Path("data/models")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_name = "finance-chat.Q4_K_M.gguf"
    model_path = model_dir / model_name

    # Skip download if model already exists
    if model_path.exists():
        print(f"Model already exists at {model_path}")
        return str(model_path)

    print(f"Downloading {model_name} to {model_path}...")

    try:
        # Download from TheBloke's Hugging Face repo
        downloaded_path = hf_hub_download(
            repo_id="TheBloke/finance-chat-GGUF",
            filename=model_name,
            local_dir=str(model_dir),
            local_dir_use_symlinks=False,
        )
        print(f"Model downloaded successfully to {downloaded_path}")
        return downloaded_path
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        # Try alternative download method if HF Hub fails
        try:
            print("Attempting direct download as fallback...")
            import urllib.request

            url = f"https://huggingface.co/TheBloke/finance-chat-GGUF/resolve/main/{model_name}"
            urllib.request.urlretrieve(url, model_path)
            print(f"Model downloaded successfully via direct URL to {model_path}")
            return str(model_path)
        except Exception as e2:
            print(f"Direct download also failed: {str(e2)}")
            raise


if __name__ == "__main__":
    download_finance_model()
