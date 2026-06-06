#!/usr/bin/env python3
"""配置诊断 - 依赖检查 + 配置完备度"""

import argparse
import json
import os
import sys
import importlib
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def check_python_version() -> Dict[str, Any]:
    """检查Python版本"""
    version = sys.version_info
    return {
        "version": f"{version.major}.{version.minor}.{version.micro}",
        "ok": version >= (3, 8),
        "required": ">=3.8",
    }


def check_node_version() -> Dict[str, Any]:
    """检查Node.js版本"""
    import subprocess
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=5
        )
        version = result.stdout.strip()
        major = int(version.lstrip("v").split(".")[0])
        return {"version": version, "ok": major >= 18, "required": ">=18"}
    except FileNotFoundError:
        return {"version": None, "ok": False, "required": ">=18", "error": "Node.js not found"}
    except Exception as e:
        return {"version": None, "ok": False, "required": ">=18", "error": str(e)}


def check_python_packages() -> List[Dict[str, Any]]:
    """检查Python依赖"""
    packages = [
        ("requests", "requests"),
        ("yaml", "PyYAML"),
        ("markdown", "markdown"),
        ("jinja2", "Jinja2"),
        ("PIL", "Pillow"),
        ("bs4", "beautifulsoup4"),
        ("lxml", "lxml"),
        ("openai", "openai"),
    ]

    results = []
    for module_name, package_name in packages:
        try:
            mod = importlib.import_module(module_name)
            version = getattr(mod, "__version__", "installed")
            results.append({
                "package": package_name,
                "module": module_name,
                "version": version,
                "ok": True,
            })
        except ImportError:
            results.append({
                "package": package_name,
                "module": module_name,
                "version": None,
                "ok": False,
            })

    return results


def check_config_file(filepath: str) -> Dict[str, Any]:
    """检查配置文件"""
    result = {"path": filepath, "exists": False, "valid": False, "missing_keys": []}

    if not os.path.exists(filepath):
        result["missing_keys"] = ["file_not_found"]
        return result

    result["exists"] = True

    try:
        import yaml
        with open(filepath, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    except ImportError:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            result["missing_keys"] = ["parse_error"]
            return result
    except Exception as e:
        result["missing_keys"] = [f"parse_error: {e}"]
        return result

    # 检查必要字段
    required_keys = {
        "wechat.appid": lambda c: c.get("wechat", {}).get("appid"),
        "wechat.secret": lambda c: c.get("wechat", {}).get("secret"),
    }

    for key, getter in required_keys.items():
        if not getter(config):
            result["missing_keys"].append(key)

    result["valid"] = len(result["missing_keys"]) == 0
    return result


def check_env_file() -> Dict[str, Any]:
    """检查.env文件"""
    env_path = ".env"
    result = {"path": env_path, "exists": False, "missing_keys": []}

    if not os.path.exists(env_path):
        result["missing_keys"] = ["file_not_found"]
        return result

    result["exists"] = True

    required_vars = [
        "WECHAT_APPID",
        "WECHAT_SECRET",
    ]

    found_vars = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=", 1)[0].strip()
                value = line.split("=", 1)[1].strip()
                found_vars[key] = bool(value)

    for var in required_vars:
        if var not in found_vars or not found_vars[var]:
            result["missing_keys"].append(var)

    result["valid"] = len(result["missing_keys"]) == 0
    return result


def check_directories() -> List[Dict[str, Any]]:
    """检查必要目录"""
    dirs = ["scripts", "toolkit", "personas"]
    results = []
    for d in dirs:
        exists = os.path.isdir(d)
        results.append({"directory": d, "exists": exists, "ok": exists})
    return results


def calculate_readiness(checks: Dict[str, Any]) -> int:
    """计算配置完备度（0-100）"""
    total = 0
    passed = 0

    # Python版本
    total += 1
    if checks.get("python_version", {}).get("ok"):
        passed += 1

    # Node版本
    total += 1
    if checks.get("node_version", {}).get("ok"):
        passed += 1

    # Python包
    pkgs = checks.get("python_packages", [])
    total += len(pkgs)
    passed += sum(1 for p in pkgs if p["ok"])

    # 配置文件
    cfg = checks.get("config_file", {})
    total += 1
    if cfg.get("valid"):
        passed += 1

    # .env文件
    env = checks.get("env_file", {})
    total += 1
    if env.get("valid"):
        passed += 1

    # 目录
    dirs = checks.get("directories", [])
    total += len(dirs)
    passed += sum(1 for d in dirs if d.get("ok"))

    return round(passed / max(total, 1) * 100)


def main():
    parser = argparse.ArgumentParser(description="配置诊断")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复")
    args = parser.parse_args()

    checks = {
        "python_version": check_python_version(),
        "node_version": check_node_version(),
        "python_packages": check_python_packages(),
        "config_file": check_config_file(args.config),
        "env_file": check_env_file(),
        "directories": check_directories(),
    }

    readiness = calculate_readiness(checks)
    checks["readiness"] = readiness

    if args.json:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        print(f"配置完备度: {readiness}%\n")

        # Python版本
        pv = checks["python_version"]
        status = "OK" if pv["ok"] else "FAIL"
        print(f"[{status}] Python {pv['version']} (required: {pv['required']})")

        # Node版本
        nv = checks["node_version"]
        status = "OK" if nv["ok"] else "FAIL"
        ver = nv.get("version", nv.get("error", "not found"))
        print(f"[{status}] Node.js {ver} (required: {nv['required']})")

        # Python包
        print("\nPython包:")
        for pkg in checks["python_packages"]:
            status = "OK" if pkg["ok"] else "MISS"
            ver = pkg.get("version", "not installed")
            print(f"  [{status}] {pkg['package']} ({ver})")

        # 配置文件
        print(f"\n配置文件 ({args.config}):")
        cf = checks["config_file"]
        status = "OK" if cf.get("valid") else "WARN"
        if cf.get("missing_keys"):
            print(f"  [{status}] 缺少: {', '.join(cf['missing_keys'])}")
        else:
            print(f"  [OK] 配置完整")

        # .env
        print("\n环境变量 (.env):")
        ef = checks["env_file"]
        if ef.get("missing_keys"):
            print(f"  [WARN] 缺少: {', '.join(ef['missing_keys'])}")
        else:
            print(f"  [OK] 环境变量完整")

        # 目录
        print("\n目录:")
        for d in checks["directories"]:
            status = "OK" if d["ok"] else "MISS"
            print(f"  [{status}] {d['directory']}")


if __name__ == "__main__":
    main()
