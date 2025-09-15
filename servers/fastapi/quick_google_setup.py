#!/usr/bin/env python3
"""
Google Gemini快速设置脚本
一键配置Google Gemini环境变量
"""

import os
import sys
import getpass

def get_google_key():
    """获取Google API密钥"""
    print("🔑 Google Gemini API密钥设置")
    print("-" * 40)
    print("如果还没有API密钥：")
    print("1. 访问: https://makersuite.google.com/app/apikey")
    print("2. 登录Google账户")
    print("3. 点击'Create API key'")
    print("4. 复制生成的API密钥")
    print()

    while True:
        key = getpass.getpass("请输入Google API密钥: ").strip()

        if not key:
            print("❌ API密钥不能为空")
            continue

        if not key.startswith("AIza"):
            print("⚠️ Google API密钥通常以'AIza'开头，请确认这是正确的密钥")
            confirm = input("确认继续? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                continue

        return key

def select_model():
    """选择默认模型"""
    print("\n🤖 选择Google Gemini模型")
    print("-" * 40)

    models = {
        "1": ("gemini-1.5-flash", "Gemini 1.5 Flash", "速度最快，成本最低，推荐日常使用"),
        "2": ("gemini-1.5-pro", "Gemini 1.5 Pro", "高性能模型，复杂任务首选"),
        "3": ("gemini-pro", "Gemini Pro", "经典模型，稳定可靠"),
    }

    for key, (model, name, desc) in models.items():
        print(f"{key}. {name} - {desc}")

    while True:
        choice = input("\n请选择模型 (1-3): ").strip()

        if choice in models:
            model, name, _ = models[choice]
            print(f"✅ 选择: {name} ({model})")
            return model
        else:
            print("❌ 无效选择，请重新输入")

def create_env_file(api_key, model):
    """创建.env文件"""
    env_content = f"""# Google Gemini配置
LLM=google
GOOGLE_API_KEY={api_key}
GOOGLE_MODEL={model}

# 可选配置
# GOOGLE_MODEL=gemini-1.5-flash
# GOOGLE_MODEL=gemini-1.5-pro
# GOOGLE_MODEL=gemini-pro
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ 已创建 .env 配置文件")

def create_bashrc_entry(api_key, model):
    """创建bashrc条目"""
    bashrc_content = f"""
# Google Gemini配置
export LLM=google
export GOOGLE_API_KEY={api_key}
export GOOGLE_MODEL={model}
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
    os.environ['LLM'] = 'google'
    os.environ['GOOGLE_API_KEY'] = api_key
    os.environ['GOOGLE_MODEL'] = model

    try:
        sys.path.insert(0, '.')
        from utils.llm_provider import get_llm_provider, is_google_selected
        from utils.get_env import get_google_api_key_env, get_google_model_env

        provider = get_llm_provider()
        is_google = is_google_selected()
        key_configured = bool(get_google_api_key_env())
        model_configured = get_google_model_env()

        if provider.name == 'GOOGLE' and is_google and key_configured:
            print("✅ 配置测试通过")
            print(f"   提供商: {provider.name}")
            print(f"   模型: {model_configured}")
            print(f"   API密钥: 已配置 ({get_google_api_key_env()[:20]}...)")
            return True
        else:
            print("❌ 配置测试失败")
            return False

    except Exception as e:
        print(f"❌ 配置测试出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Google Gemini快速设置向导")
    print("=" * 50)
    print("这个脚本将帮你快速配置Google Gemini")
    print("让Presenton使用Google的强大AI模型")
    print("=" * 50)

    global api_key, model

    # 获取API密钥
    api_key = get_google_key()

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
        print("  curl -X POST http://localhost:8000/api/v3/ppt/presentation/generate \\")
        print("       -H 'Content-Type: application/json' \\")
        print("       -d '{\"user_input\": \"人工智能发展趋势\", \"template\": \"modern\"}'")
        print("")
        print("💡 Google Gemini特点:")
        print("• 多模态支持（文本、图片、视频）")
        print("• 强大的代码生成能力")
        print("• 免费额度充足")
        print("• Google官方支持，稳定可靠")
    else:
        print("\n❌ 配置可能有问题，请检查设置")

if __name__ == "__main__":
    main()

