import os
import google.generativeai as genai
import subprocess
import sys


def get_diff():
    """获取 git diff 用于当前分支。"""
    try:
        result = subprocess.run(['git', 'diff'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"获取 git diff 失败，返回码：{e.returncode}，错误信息：{e.stderr}")
        sys.exit(1)


def analyze_with_gemini(code_diff, api_key):
    """使用 Gemini API 分析代码差异。"""
    if not api_key:
        print("错误：API 密钥为空。请确保设置了 GEMINI_API_KEY 环境变量。")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
作为一名资深代码审查员，你的任务是帮助开发者改进代码质量。请详细分析以下代码差异，
并提供清晰、可操作的反馈。请注意以下几点：

1.  **关注代码质量：** 检查代码的可读性、可维护性、性能和安全性。
2.  **提供具体建议：** 避免泛泛而谈，给出明确的代码改进建议，最好能包含修改后的代码示例。
3.  **遵循最佳实践：** 确保代码遵循通用的编码规范和最佳实践。
4.  **考虑上下文：** 在分析代码时，要考虑到代码的实际用途和项目背景。
5.  **语言风格：** 使用专业、友好的语言，避免使用过于严厉或指责性的措辞。
6.  **输出格式：** 你的回复应该包含以下部分：
    *   **概述 (Overview)：** 简要总结代码变更的目的。
    *   **详细分析 (Detailed Analysis)：** 逐条列出代码中存在的问题，并给出修改建议。每条建议都需要包含：
        *   **问题描述 (Problem Description)：** 详细描述代码中存在的问题。
        *   **建议 (Suggestion)：** 给出具体的修改建议。
        *   **修改后的代码 (Improved Code)：** 如果可能，提供修改后的代码示例，使用 Markdown 代码块包裹。
    *   **总结 (Summary)：** 总结本次代码审查的重点。

请分析以下代码差异：

```diff
{code_diff}
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API 调用期间出错：{e}")
        return None


def escape_for_github_actions(input_string):
    """转义要用于 GitHub Actions 输出的特殊字符。"""
    escaped_string = input_string.replace('%', '%25').replace('\n', '%0A').replace('\r', '%0D')
    return escaped_string


def main():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("错误：未设置 GEMINI_API_KEY。")
        sys.exit(1)

    code_diff = get_diff()
    if not code_diff:
        print("未找到任何代码差异。")
        sys.exit(0)

    gemini_analysis = analyze_with_gemini(code_diff, api_key)

    if gemini_analysis:
        print("Gemini 代码审核：\n", gemini_analysis)

        # 正确转义输出以供 GitHub Actions 使用
        escaped_analysis = escape_for_github_actions(gemini_analysis)
        print(f"::set-output name=issue_body::{escaped_analysis}")


if __name__ == "__main__":
    main()
