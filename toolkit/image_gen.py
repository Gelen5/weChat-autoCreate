#!/usr/bin/env python3
"""9提供商图片生成 - doubao/openai/gemini/dashscope/minimax/replicate/azure_openai/openrouter/jimeng"""

import json
import os
import time
import base64
import logging
from typing import Dict, Any, Optional, List

import requests

from .config import get_config, Config

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


class ImageGenerator:
    """多提供商图片生成"""

    PROVIDERS = [
        "doubao", "openai", "gemini", "dashscope", "minimax",
        "replicate", "azure_openai", "openrouter", "jimeng",
    ]

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()

    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        size: str = "1024x1024",
        output_dir: str = "./output",
    ) -> Optional[str]:
        """生成图片"""
        provider = provider or self.config.image_provider
        model = model or self._get_default_model(provider)

        if provider not in self.PROVIDERS:
            logger.error(f"不支持的提供商: {provider}，可选: {', '.join(self.PROVIDERS)}")
            return None

        logger.info(f"使用 {provider}/{model} 生成图片: {prompt[:50]}...")

        for attempt in range(MAX_RETRIES):
            try:
                result = self._dispatch(provider, prompt, model, size, output_dir)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"尝试 {attempt + 1}/{MAX_RETRIES} 失败: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)

        logger.error("所有重试均失败")
        return None

    def _get_default_model(self, provider: str) -> str:
        defaults = {
            "openai": "dall-e-3",
            "doubao": "doubao-seedream-3-0-t2i-250415",
            "gemini": "imagen-3.0-generate-001",
            "dashscope": "wanx-v1",
            "minimax": "image-01",
            "replicate": "stability-ai/sdxl",
            "azure_openai": "dall-e-3",
            "openrouter": "openai/dall-e-3",
            "jimeng": "jimeng-2.1",
        }
        return defaults.get(provider, "dall-e-3")

    def _dispatch(
        self, provider: str, prompt: str, model: str, size: str, output_dir: str
    ) -> Optional[str]:
        """分发到对应提供商"""
        dispatch_map = {
            "openai": self._gen_openai,
            "doubao": self._gen_doubao,
            "gemini": self._gen_gemini,
            "dashscope": self._gen_dashscope,
            "minimax": self._gen_minimax,
            "replicate": self._gen_replicate,
            "azure_openai": self._gen_azure_openai,
            "openrouter": self._gen_openrouter,
            "jimeng": self._gen_jimeng,
        }

        handler = dispatch_map.get(provider)
        if not handler:
            return None

        image_data = handler(prompt, model, size)
        if not image_data:
            return None

        return self._save_image(image_data, output_dir)

    def _get_api_key(self, provider: str) -> str:
        """获取API Key"""
        env_map = {
            "openai": "OPENAI_API_KEY",
            "doubao": "DOUBAO_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "dashscope": "DASHSCOPE_API_KEY",
            "minimax": "MINIMAX_API_KEY",
            "replicate": "REPLICATE_API_TOKEN",
            "azure_openai": "AZURE_OPENAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "jimeng": "JIMENG_API_KEY",
        }

        env_var = env_map.get(provider, "")
        key = os.environ.get(env_var)
        if key:
            return key

        # 从配置文件读取
        key = self.config.get(f"image.{provider}.api_key", "")
        if key:
            return key

        # 通用image配置
        key = self.config.get("image.api_key", "")
        return key

    def _save_image(self, image_data: bytes, output_dir: str) -> str:
        """保存图片"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"gen_{int(time.time())}_{id(image_data) % 10000}.png"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)
        logger.info(f"图片已保存: {filepath}")
        return filepath

    # ── 各提供商实现 ──

    def _gen_openai(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """OpenAI DALL-E"""
        api_key = self._get_api_key("openai")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 未设置")

        resp = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": size,
                "response_format": "b64_json",
            },
            timeout=120,
        )
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"OpenAI错误: {data['error'].get('message', 'unknown')}")

        b64 = data["data"][0].get("b64_json")
        if b64:
            return base64.b64decode(b64)

        url = data["data"][0].get("url")
        if url:
            img_resp = requests.get(url, timeout=30)
            return img_resp.content

        return None

    def _gen_doubao(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """字节豆包"""
        api_key = self._get_api_key("doubao")
        if not api_key:
            raise ValueError("DOUBAO_API_KEY 未设置")

        resp = requests.post(
            "https://visual.volcengineapi.com/",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "req_key": "high_aes",
                "model": model,
                "prompt": prompt,
                "return_url": False,
                "logo_info": {"add_logo": False},
            },
            timeout=120,
        )
        data = resp.json()
        if data.get("code") != 10000:
            raise RuntimeError(f"豆包错误: {data.get('msg', 'unknown')}")

        b64 = data.get("data", {}).get("binary_data_base64", [""])[0]
        if b64:
            return base64.b64decode(b64)

        return None

    def _gen_gemini(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """Google Gemini/Imagen"""
        api_key = self._get_api_key("gemini")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 未设置")

        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict",
            params={"key": api_key},
            json={
                "instances": [{"prompt": prompt}],
                "parameters": {"sampleCount": 1},
            },
            timeout=120,
        )
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"Gemini错误: {data['error'].get('message', 'unknown')}")

        predictions = data.get("predictions", [])
        if predictions:
            b64 = predictions[0].get("bytesBase64Encoded", "")
            if b64:
                return base64.b64decode(b64)

        return None

    def _gen_dashscope(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """阿里通义万相"""
        api_key = self._get_api_key("dashscope")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY 未设置")

        # 提交任务
        resp = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            },
            json={
                "model": model,
                "input": {"prompt": prompt},
                "parameters": {"size": size, "n": 1},
            },
            timeout=60,
        )
        data = resp.json()
        task_id = data.get("output", {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"通义万相提交失败: {data}")

        # 轮询结果
        for _ in range(60):
            time.sleep(2)
            poll_resp = requests.get(
                f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            poll_data = poll_resp.json()
            status = poll_data.get("output", {}).get("task_status")
            if status == "SUCCEEDED":
                url = poll_data["output"]["results"][0]["url"]
                img_resp = requests.get(url, timeout=30)
                return img_resp.content
            elif status == "FAILED":
                raise RuntimeError("通义万相生成失败")

        raise RuntimeError("通义万相超时")

    def _gen_minimax(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """MiniMax"""
        api_key = self._get_api_key("minimax")
        if not api_key:
            raise ValueError("MINIMAX_API_KEY 未设置")

        group_id = os.environ.get("MINIMAX_GROUP_ID", self.config.get("image.minimax.group_id", ""))

        resp = requests.post(
            f"https://api.minimax.chat/v1/text/image?GroupId={group_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "prompt": prompt,
            },
            timeout=120,
        )
        data = resp.json()
        if data.get("base_resp", {}).get("status_code") != 0:
            raise RuntimeError(f"MiniMax错误: {data.get('base_resp', {}).get('status_msg', 'unknown')}")

        url = data.get("data", {}).get("image_url")
        if url:
            img_resp = requests.get(url, timeout=30)
            return img_resp.content

        return None

    def _gen_replicate(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """Replicate"""
        api_key = self._get_api_key("replicate")
        if not api_key:
            raise ValueError("REPLICATE_API_TOKEN 未设置")

        resp = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={"Authorization": f"Token {api_key}"},
            json={
                "version": model,
                "input": {"prompt": prompt, "width": 1024, "height": 1024},
            },
            timeout=60,
        )
        data = resp.json()
        poll_url = data.get("urls", {}).get("get")
        if not poll_url:
            raise RuntimeError("Replicate提交失败")

        # 轮询
        for _ in range(120):
            time.sleep(2)
            poll_resp = requests.get(
                poll_url,
                headers={"Authorization": f"Token {api_key}"},
                timeout=10,
            )
            poll_data = poll_resp.json()
            if poll_data.get("status") == "succeeded":
                output = poll_data.get("output")
                if isinstance(output, list) and output:
                    url = output[0]
                elif isinstance(output, str):
                    url = output
                else:
                    return None
                img_resp = requests.get(url, timeout=30)
                return img_resp.content
            elif poll_data.get("status") == "failed":
                raise RuntimeError("Replicate生成失败")

        raise RuntimeError("Replicate超时")

    def _gen_azure_openai(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """Azure OpenAI"""
        api_key = self._get_api_key("azure_openai")
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY 未设置")

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", self.config.get("image.azure_openai.endpoint", ""))
        api_version = "2024-02-15-preview"

        url = f"{endpoint}/openai/deployments/{model}/images/generations?api-version={api_version}"

        resp = requests.post(
            url,
            headers={"api-key": api_key, "Content-Type": "application/json"},
            json={"prompt": prompt, "n": 1, "size": size},
            timeout=120,
        )
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"Azure OpenAI错误: {data['error'].get('message', 'unknown')}")

        img_url = data.get("data", [{}])[0].get("url")
        if img_url:
            img_resp = requests.get(img_url, timeout=30)
            return img_resp.content

        return None

    def _gen_openrouter(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """OpenRouter"""
        api_key = self._get_api_key("openrouter")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY 未设置")

        resp = requests.post(
            "https://openrouter.ai/api/v1/images/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": size,
            },
            timeout=120,
        )
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"OpenRouter错误: {data['error'].get('message', 'unknown')}")

        img_url = data.get("data", [{}])[0].get("url")
        if img_url:
            img_resp = requests.get(img_url, timeout=30)
            return img_resp.content

        return None

    def _gen_jimeng(self, prompt: str, model: str, size: str) -> Optional[bytes]:
        """即梦（字节跳动）"""
        api_key = self._get_api_key("jimeng")
        if not api_key:
            raise ValueError("JIMENG_API_KEY 未设置")

        resp = requests.post(
            "https://jimeng.jianying.com/mdream/v1/paint",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
            },
            timeout=120,
        )
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"即梦错误: {data.get('msg', 'unknown')}")

        img_url = data.get("data", {}).get("img_url")
        if img_url:
            img_resp = requests.get(img_url, timeout=30)
            return img_resp.content

        return None
