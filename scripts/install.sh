#!/usr/bin/env bash
# 安装脚本 - venv隔离
# 支持 macOS/Linux/Windows(WSL)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo "=== 微信公众号全链路自动化 - 安装脚本 ==="
echo ""

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="macos";;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows";;
    *)          PLATFORM="unknown";;
esac

echo "检测平台: ${PLATFORM}"

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "错误: 未找到Python，请安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python版本: ${PYTHON_VERSION}"

# 检查Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "Node.js版本: ${NODE_VERSION}"
else
    echo "警告: 未找到Node.js，TypeScript脚本将不可用"
fi

# ── Python环境 ──
echo ""
echo "=== 设置Python虚拟环境 ==="

if [ -d "${VENV_DIR}" ]; then
    echo "虚拟环境已存在: ${VENV_DIR}"
else
    echo "创建虚拟环境..."
    $PYTHON -m venv "${VENV_DIR}"
fi

# 激活虚拟环境
if [ "${PLATFORM}" = "windows" ]; then
    source "${VENV_DIR}/Scripts/activate"
else
    source "${VENV_DIR}/bin/activate"
fi

echo "安装Python依赖..."
pip install --upgrade pip -q
pip install -r "${SCRIPT_DIR}/requirements.txt" -q

echo "Python环境设置完成"

# ── Node.js环境 ──
if command -v node &> /dev/null; then
    echo ""
    echo "=== 设置Node.js环境 ==="

    if [ -f "${SCRIPT_DIR}/package.json" ]; then
        echo "安装Node.js依赖..."
        cd "${SCRIPT_DIR}"

        if command -v pnpm &> /dev/null; then
            pnpm install
        elif command -v yarn &> /dev/null; then
            yarn install
        else
            npm install
        fi

        echo "Node.js环境设置完成"
    fi
fi

# ── 验证 ──
echo ""
echo "=== 验证安装 ==="

$PYTHON -c "import requests; print(f'requests {requests.__version__} OK')" 2>/dev/null || echo "requests: FAIL"
$PYTHON -c "import yaml; print(f'PyYAML OK')" 2>/dev/null || echo "PyYAML: FAIL"
$PYTHON -c "import markdown; print(f'markdown {markdown.__version__} OK')" 2>/dev/null || echo "markdown: FAIL"

if command -v node &> /dev/null; then
    node -e "try { require('marked'); console.log('marked OK'); } catch(e) { console.log('marked: FAIL'); }" 2>/dev/null || true
fi

echo ""
echo "=== 安装完成 ==="
echo ""
echo "使用方法:"
echo "  Python: source ${VENV_DIR}/bin/activate  # 激活虚拟环境"
echo "  Python: python scripts/fetch_hotspots.py --limit 10"
echo "  Node:   npx ts-node scripts/publish.ts article.md"
echo ""
echo "首次使用请复制配置模板:"
echo "  cp config.example.yaml config.yaml"
echo "  cp .env.example .env"
echo "  编辑 config.yaml 和 .env 填入API凭证"
