import requests
import sys
import subprocess
import os

url = "https://api.siliconflow.cn/v1/chat/completions"

# 获取代码文件名（不包括扩展名）
code_filename = os.path.splitext(sys.argv[1])[0]

# 修复变量名冲突问题
with open('./include/codefile.l', 'r', encoding='utf-8') as codefile_file:
    codefile = codefile_file.read()

with open(sys.argv[1], 'r', encoding='utf-8') as userfile:
    user_content = userfile.read()

payload = {
    "model": "Qwen/Qwen3-8B",
    "messages": [
        {
            "role": "user",
            "content": (
                "你是一个叫'l code'的代码编译器。\n"
                "这是定义头文件的内容:\n" + codefile + "\n"
                "这是用户写的内容:\n" + user_content + "\n"
                "请根据内容生成C语言代码。要求只返回代码本身，不要其他说明。"
            )
        }
    ],
    "max_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.7,
    "frequency_penalty": 0.5,
    "n": 1,
    "response_format": {"type": "text"},
    "enable_thinking": False
}

headers = {
    "Authorization": "Bearer sk-pcqfmqgqgvvvttinzfkmdzltfhwectodzzieiaenwhcgwcax",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

# 检查是否是函数调用类型的响应
if "tool_calls" in response.json():
    tool_calls = response.json()["tool_calls"]
    for tool in tool_calls:
        if tool["type"] == "function":
            function_name = tool["function"]["name"]
            arguments = tool["function"]["arguments"]
            if "打印字符串" in function_name:
                # 根据函数调用生成C语言代码
                string_to_print = arguments.get("字符串", "俱乐部规律")
                generated_code = f'#include <stdio.h>\n\nint main() {{\n    printf("{string_to_print}\\n");\n    return 0;\n}}'
                print("生成的代码:")
                print(generated_code)
                
                # 将生成的代码写入文件
                with open(f"{code_filename}.c", "w", encoding="utf-8") as code_file:
                    code_file.write(generated_code)
                
                # 使用gcc编译代码
                compile_result = subprocess.run(
                    ["gcc", f"{code_filename}.c", "-o", f"{code_filename}_program"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                print("\n编译结果:")
                print(compile_result.stdout)
                print(compile_result.stderr)
                
                # 如果编译成功，删除.c文件
                if compile_result.returncode == 0:
                    os.remove(f"{code_filename}.c")
                    print(f"\n已删除 {code_filename}.c 文件")
                    
                    # 运行生成的程序
                    if os.name == "nt":
                        run_result = subprocess.run(
                            [f"{code_filename}_program.exe"],
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='replace'
                        )
                    else:
                        run_result = subprocess.run(
                            [f"./{code_filename}_program"],
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='replace'
                        )
                    print("\n程序运行结果:")
                    print(run_result.stdout)
                    print(run_result.stderr)
                else:
                    print("\n编译失败，不删除.c文件也不执行程序运行")
else:
    # 检查是否直接返回了代码
    response_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    if "printf" in response_text or "#include" in response_text:
        print("API直接返回了代码:")
        print(response_text)
        
        # 将生成的代码写入文件
        with open(f"{code_filename}.c", "w", encoding="utf-8") as code_file:
            code_file.write(response_text)
        
        # 使用gcc编译代码
        compile_result = subprocess.run(
            ["gcc", f"{code_filename}.c", "-o", f"{code_filename}_program"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print("\n编译结果:")
        print(compile_result.stdout)
        print(compile_result.stderr)
        
        # 如果编译成功，删除.c文件
        if compile_result.returncode == 0:
            os.remove(f"{code_filename}.c")
            print(f"\n已删除 {code_filename}.c 文件")
            
            # 运行生成的程序
            if os.name == "nt":
                run_result = subprocess.run(
                    [f"{code_filename}_program.exe"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                run_result = subprocess.run(
                    [f"./{code_filename}_program"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            print("\n程序运行结果:")
            print(run_result.stdout)
            print(run_result.stderr)
        else:
            print("\n编译失败，不删除.c文件也不执行程序运行")
    else:
        print("API未生成代码。尝试重新描述需求...")
