#!/usr/bin/env python3
"""
OpenRouter快速设置脚本
一键配置OpenRouter环境变量
"""

import os
import sys
import getpass

def get_openrouter_key():
    """获取OpenRouter API密钥"""
    print("🔑 OpenRouter API密钥设置")
    print("-" * 40)
    print("如果还没有API密钥：")
    print("1. 访问: https://openrouter.ai/")
    print("2. 注册/登录账户")
    print("3. 进入Dashboard获取API密钥")
    print("4. 为账户充值（支持多种支付方式）")
    print()

    while True:
        key = getpass.getpass("请输入OpenRouter API密钥 (sk-or-v1-...): ").strip()

        if not key:
            print("❌ API密钥不能为空")
            continue

        if not key.startswith("sk-or-v1-"):
            print("❌ API密钥格式不正确，应该以 'sk-or-v1-' 开头")
            continue

        return key

def select_model():
    """选择默认模型"""
    print("\n🤖 选择默认模型")
    print("-" * 40)

    models = {
        "1": ("anthropic/claude-3-haiku:beta", "Claude 3 Haiku", "性价比最高，推荐新手"),
        "2": ("openai/gpt-4o-mini", "GPT-4o Mini", "OpenAI最便宜，响应快速"),
        "3": ("google/gemini-flash-1.5", "Gemini Flash 1.5", "Google最便宜，速度超快"),
        "4": ("anthropic/claude-3.5-sonnet:beta", "Claude 3.5 Sonnet", "高性能，复杂任务首选"),
        "5": ("meta/llama-3.1-8b-instruct", "Llama 3.1 8B", "免费模型，体验使用"),
    }

    for key, (model, name, desc) in models.items():
        print(f"{key}. {name} - {desc}")

    while True:
        choice = input("\n请选择模型 (1-5): ").strip()

        if choice in models:
            model, name, _ = models[choice]
            print(f"✅ 选择: {name} ({model})")
            return model
        else:
            print("❌ 无效选择，请重新输入")

def create_env_file(api_key, model):
    """创建.env文件"""
    env_content = f"""# OpenRouter配置
LLM=openrouter
OPENROUTER_API_KEY={api_key}
OPENROUTER_MODEL={model}

# 可选配置
# OPENROUTER_MODEL=anthropic/claude-3-haiku:beta
# OPENROUTER_MODEL=openai/gpt-4o-mini
# OPENROUTER_MODEL=google/gemini-flash-1.5
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ 已创建 .env 配置文件")

def create_bashrc_entry(api_key, model):
    """创建bashrc条目"""
    bashrc_content = f"""
# OpenRouter配置
export LLM=openrouter
export OPENROUTER_API_KEY={api_key}
export OPENROUTER_MODEL={model}
"""

    bashrc_path = os.path.expanduser('~/.bashrc')
    with open(bashrc_path, 'a') as f:
        f.write(bashrc_content)

    print(f"✅ 已添加到 {bashrc_path}")

def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置")
    print("-" * 40)

    # 设置环境变量
    os.environ['LLM'] = 'openrouter'
    os.environ['OPENROUTER_API_KEY'] = api_key
    os.environ['OPENROUTER_MODEL'] = model

    try:
        sys.path.insert(0, '.')
        from utils.llm_provider import get_llm_provider, is_openrouter_selected
        from utils.get_env import get_openrouter_api_key_env, get_openrouter_model_env

        provider = get_llm_provider()
        is_openrouter = is_openrouter_selected()
        key_configured = bool(get_openrouter_api_key_env())
        model_configured = get_openrouter_model_env()

        if provider.name == 'OPENROUTER' and is_openrouter and key_configured:
            print("✅ 配置测试通过")
            print(f"   提供商: {provider.name}")
            print(f"   模型: {model_configured}")
            print(f"   API密钥: 已配置 ({get_openrouter_api_key_env()[:20]}...)")
            return True
        else:
            print("❌ 配置测试失败")
            return False

    except Exception as e:
        print(f"❌ 配置测试出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 OpenRouter快速设置向导")
    print("=" * 50)
    print("这个脚本将帮你快速配置OpenRouter")
    print("让Presenton使用多种LLM模型")
    print("=" * 50)

    global api_key, model

    # 获取API密钥
    api_key = get_openrouter_key()

    # 选择模型
    model = select_model()

    # 创建配置文件
    print("\n📝 创建配置文件")
    print("-" * 40)

    # 选项1: 创建.env文件
    create_env = input("是否创建.env配置文件? (y/n): ").strip().lower()
    if create_env in ['y', 'yes']:
        create_env_file(api_key, model)

    # 选项2: 添加到bashrc
    add_bashrc = input("是否添加到~/.bashrc? (y/n): ").strip().lower()
    if add_bashrc in ['y', 'yes']:
        create_bashrc_entry(api_key, model)

    # 测试配置
    if test_configuration():
        print("\n🎉 配置完成！")
        print("=" * 50)
        print("现在你可以运行以下命令启动Presenton:")
        print("  python start_v3_demo.py")
        print("")
        print("或者直接运行:")
        print("  python server.py --port 8000")
        print("")
        print("测试API:")
        print("  python test_openrouter.py")
        print("")
        print("查看演示:")
        print("  python demo_openrouter.py")
    else:
        print("\n❌ 配置可能有问题，请检查设置")

if __name__ == "__main__":
    main()
