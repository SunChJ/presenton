import asyncio
import os
import aiohttp
from google import genai
from google.genai.types import GenerateContentConfig
from openai import AsyncOpenAI
from models.image_prompt import ImagePrompt
from models.sql.image_asset import ImageAsset
from utils.download_helpers import download_file
from utils.get_env import get_pexels_api_key_env
from utils.get_env import get_pixabay_api_key_env
from utils.image_provider import (
    is_pixels_selected,
    is_pixabay_selected,
    is_gemini_flash_selected,
    is_dalle3_selected,
)
import uuid


class ImageGenerationService:

    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.image_gen_func = self.get_image_gen_func()

    def get_image_gen_func(self):
        if is_pixabay_selected():
            return self.get_image_from_pixabay
        elif is_pixels_selected():
            return self.get_image_from_pexels
        elif is_gemini_flash_selected():
            return self.generate_image_google
        elif is_dalle3_selected():
            return self.generate_image_openai
        return None

    def is_stock_provider_selected(self):
        return is_pixels_selected() or is_pixabay_selected()

    async def generate_image(self, prompt: ImagePrompt) -> str | ImageAsset:
        """
        Generates an image based on the provided prompt.
        - If no image generation function is available, returns a placeholder image.
        - If the stock provider is selected, it uses the prompt directly,
        otherwise it uses the full image prompt with theme.
        - Output Directory is used for saving the generated image not the stock provider.
        """
        # Get the current image generation function (dynamic selection)
        current_image_gen_func = self.get_image_gen_func()
        
        # Debug logging
        from utils.image_provider import get_selected_image_provider
        selected_provider = get_selected_image_provider()
        print(f"Selected image provider: {selected_provider}")
        print(f"Current image generation function: {current_image_gen_func.__name__ if current_image_gen_func else None}")
        
        if not current_image_gen_func:
            print("No image generation function found. Using placeholder image.")
            return "/static/images/placeholder.jpg"

        image_prompt = prompt.get_image_prompt(
            with_theme=not self.is_stock_provider_selected()
        )
        print(f"Request - Generating Image for {image_prompt}")

        try:
            if self.is_stock_provider_selected():
                image_path = await current_image_gen_func(image_prompt)
            else:
                image_path = await current_image_gen_func(
                    image_prompt, self.output_directory
                )
            if image_path:
                if image_path.startswith("http"):
                    return image_path
                elif os.path.exists(image_path):
                    return ImageAsset(
                        path=image_path,
                        is_uploaded=False,
                        extras={
                            "prompt": prompt.prompt,
                            "theme_prompt": prompt.theme_prompt,
                        },
                    )
            raise Exception(f"Image not found at {image_path}")

        except Exception as e:
            error_message = str(e)
            
            # Check for quota/billing issues and provide helpful guidance
            if "429" in error_message and "RESOURCE_EXHAUSTED" in error_message:
                print("🚨 API QUOTA EXHAUSTED - 配额用尽提醒")
                print("=" * 60)
                print("📊 Google Gemini API配额已用完，建议:")
                print("1. 等待配额重置 (通常每日UTC 00:00重置)")
                print("2. 临时切换到其他图片提供商:")
                print("   - 修改 app_data/userConfig.json")
                print("   - 将 \"IMAGE_PROVIDER\" 改为 \"pexels\"")
                print("   - 或访问前端设置页面修改")
                print("3. 升级到付费计划: https://aistudio.google.com/")
                print("4. 当前回退到占位符图片")
                print("=" * 60)
            elif "quota" in error_message.lower() or "billing" in error_message.lower():
                print("💰 API配额/账单问题 - 请检查:")
                print("- Google Cloud Console配额设置")
                print("- 账单和付费状态")
                print("- API密钥权限")
            elif "401" in error_message or "403" in error_message:
                print("🔑 API认证问题 - 请检查:")
                print("- API密钥是否正确")
                print("- API是否已启用")
            else:
                print(f"Error generating image: {e}")
                
            return "/static/images/placeholder.jpg"

    async def generate_image_openai(self, prompt: str, output_directory: str) -> str:
        client = AsyncOpenAI()
        result = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            quality="standard",
            size="1024x1024",
        )
        image_url = result.data[0].url
        return await download_file(image_url, output_directory)

    async def generate_image_google(self, prompt: str, output_directory: str) -> str:
        client = genai.Client()
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash-image-preview",
            contents=[prompt],
            config=GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image_path = os.path.join(output_directory, f"{uuid.uuid4()}.jpg")
                with open(image_path, "wb") as f:
                    f.write(part.inline_data.data)

        return image_path

    async def get_image_from_pexels(self, prompt: str) -> str:
        async with aiohttp.ClientSession(trust_env=True) as session:
            response = await session.get(
                f"https://api.pexels.com/v1/search?query={prompt}&per_page=1",
                headers={"Authorization": f"{get_pexels_api_key_env()}"},
            )
            
            # Check HTTP status
            if response.status != 200:
                raise Exception(f"Pexels API error: HTTP {response.status}")
            
            data = await response.json()
            
            # Check if the response contains photos
            if "photos" not in data or not data["photos"]:
                raise Exception(f"No photos found for prompt: {prompt}")
            
            image_url = data["photos"][0]["src"]["large"]
            return image_url

    async def get_image_from_pixabay(self, prompt: str) -> str:
        async with aiohttp.ClientSession(trust_env=True) as session:
            response = await session.get(
                f"https://pixabay.com/api/?key={get_pixabay_api_key_env()}&q={prompt}&image_type=photo&per_page=3"
            )
            
            # Check HTTP status
            if response.status != 200:
                raise Exception(f"Pixabay API error: HTTP {response.status}")
            
            data = await response.json()
            
            # Check if the response contains hits
            if "hits" not in data or not data["hits"]:
                raise Exception(f"No images found for prompt: {prompt}")
            
            image_url = data["hits"][0]["largeImageURL"]
            return image_url
