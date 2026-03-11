import os
import time
import random

try:
    from dotenv import load_dotenv
    import google.generativeai as genai
    load_dotenv()
    
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        # Using a reliable generative model for coding tasks
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        model = None
except ImportError:
    model = None

def analyze_code_snippet(code):
    """
    Analyzes code snippet for bugs. Streams response back as a generator.
    """
    if not code or len(code.strip()) == 0:
        yield "Error: No code provided for analysis."
        return
        
    if model:
        try:
            prompt = f"""
You are an expert Python developer and code reviewer. Review the following code snippet and report any logical bugs, syntax errors, or major security flaws.
Keep your response extremely simple, clear, and easy for a beginner to understand. Do NOT use any emojis.

For each issue found, format your response exactly like this:
- **Bug**: [Clearly state what the bug is]
- **Impact**: [Explain simply what errors or bad behavior this may cause]
- **Fix**: [Provide the possible fix or corrected code]

If there are no issues, just reply with: "No major bugs detected in this code snippet." Do NOT provide a Corrected Code Snippet block if there are no bugs.

CRITICAL: If you found bugs and suggested fixes, you MUST provide the entire, fully corrected version of the code snippet at the very end of your response. 
Enclose the full corrected code in a standard markdown code block (e.g., ```python ... ```).

Code to analyze:
```
{code}
```
"""
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            # Fall through to simulation if API fails

    # SIMULATION FALLBACK
    time.sleep(1)
    
    bugs: list[str] = []
    if "== True" in code or "== False" in code:
        bugs.append(
            "- **Bug**: You are comparing a value directly to `True` or `False` (e.g., `if x == True:`).\n"
            "- **Impact**: This is unnecessary and goes against standard Python styling rules (PEP 8). It makes code slightly harder to read.\n"
            "- **Fix**: Evaluate the boolean directly. Write `if x:` instead of `if x == True:`."
        )
        code = code.replace("== True", "")
        code = code.replace("== False", "not ")
    if "except:" in code:
        bugs.append(
            "- **Bug**: You are using a bare `except:` block to catch errors.\n"
            "- **Impact**: This will catch *every* error, even ones you don't expect like the user trying to exit the script. This hides true bugs and makes debugging very hard.\n"
            "- **Fix**: Catch specific errors instead, like `except ValueError:` or at least `except Exception as e:`."
        )
        code = code.replace("except:", "except Exception as e:")
    if "eval(" in code:
        bugs.append(
            "- **Bug**: The code uses the `eval()` function.\n"
            "- **Impact**: `eval()` runs whatever string you pass it as actual Python code. If a malicious user controls that string, they can hack your server or run dangerous commands.\n"
            "- **Fix**: Avoid using `eval()` completely. If you are trying to read a dictionary from a string, use standard JSON or `ast.literal_eval()`."
        )
        code = code.replace("eval(", "ast.literal_eval(")
        
    if bugs:
        report = "### AI Analysis Report (Simulated Fallback)\n\n"
        if "def " not in code and "class " not in code:
            report += "#### Architecture & Structure\n"
            report += "The provided snippet appears to be a basic script without encapsulated functions or classes.\n"
            report += "**Recommendation:** Encapsulate your logic within functions or classes. This improves reusability, testability, and prevents namespace pollution.\n\n"
        elif "def " in code:
            report += "#### Architecture & Structure\n"
            report += "Function definitions detected. The code demonstrates a basic level of modularity.\n\n"
            
        report += "Issues found in your code:\n\n"
        for bug in bugs:
            report += f"{bug}\n\n"
            
        report += "#### Summary Recommendation\n"
        report += "Please review the flagged items above. Addressing these will result in more robust, secure, and idiomatic code.\n\n"
        
        report += "### Corrected Code Snippet\n"
        report += "Here is the fully fixed version of your code:\n\n"
        report += "```python\n"
        report += code  # Provide the heuristically altered code as the fix
        report += "\n```\n"
    else:
        report = "### AI Analysis Report (Simulated Fallback)\n\n"
        report += "No major bugs detected in this code snippet. Your code looks clean and doesn't require any structural fixes."
    
    # Stream simulated output
    for chunk in report.split(' '):
        yield chunk + ' '
        time.sleep(0.04)

def generate_test_cases(code, language="python"):
    """
    Generates unit tests using Gemini. Streams response back as a generator.
    """
    if not code or len(code.strip()) == 0:
        yield "Error: No code provided to generate tests."
        return
        
    if model:
        try:
            prompt = f"""
You are an expert QA engineer. Generate a comprehensive test suite for the following {language} code snippet.
Do NOT use any emojis or conversational filler text. 
Return strictly the markdown for the generated code, starting with `#### Generated Test Suite`.
Ensure the test code is well-commented and tests boundaries, nominal cases, and error states if obvious.

Code snippet:
```
{code}
```
"""
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as e:
            print(f"Gemini generation error: {e}")
            # Fall through to simulation if API fails

    # SIMULATION FALLBACK
    time.sleep(1)
    
    if language.lower() == "python":
        tests = "#### Generated Test Suite (Simulated Fallback for Python)\n\n"
        tests += "```python\n"
        tests += "import pytest\n\n"
        tests += "# Automatically generated comprehensive test cases\n\n"
        if "def " in code:
            try:
                func_name = code.split("def ")[1].split("(")[0].strip()
                tests += f"def test_{func_name}_nominal_execution():\n"
                tests += f"    \"\"\"Verifies the {func_name} function under expected nominal conditions.\"\"\"\n"
                tests += f"    # Arrange\n"
                tests += f"    # TODO: Define test inputs\n"
                tests += f"    \n"
                tests += f"    # Act\n"
                tests += f"    # result = {func_name}(...)\n"
                tests += f"    \n"
                tests += f"    # Assert\n"
                tests += f"    # assert result == expected_output\n"
                tests += f"    assert True\n\n"
                
                tests += f"def test_{func_name}_boundary_conditions():\n"
                tests += f"    \"\"\"Validates {func_name} behavior when provided boundary or edge-case inputs.\"\"\"\n"
                tests += f"    # Arrange / Act / Assert\n"
                tests += f"    # TODO: Implement edge case scenarios\n"
                tests += f"    pass\n"
            except Exception:
                tests += "def test_executable_logic():\n    \"\"\"General test placeholder.\"\"\"\n    assert True\n"
        else:
            tests += "def test_script_execution_state():\n"
            tests += "    \"\"\"Validates the end state or side-effects of the main script.\"\"\"\n"
            tests += "    # TODO: Replace with specific assertions against module-level variables\n"
            tests += "    assert True\n"
        tests += "```\n"
        tests += "\n**Usage Instructions:** Save these tests in a `tests/` directory and execute them using `pytest` from your command line."
        
        for chunk in tests.split(' '):
            yield chunk + ' '
            time.sleep(0.04)
        return
    else:
        yield f"#### Test Suite Generation\n\nGeneration of test suites for `{language}` is currently unsupported in this environment mock."
        return
