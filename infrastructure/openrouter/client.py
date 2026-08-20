import os
import json
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except Exception:
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None

try:
    from core.prompt import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = "You are a helpful assistant."
except Exception:
    SYSTEM_PROMPT = "You are a helpful assistant."

# Load environment variables from a .env file
load_dotenv()


class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        if OpenAI is None:
            raise ImportError("openai package is required to instantiate OpenRouterClient")

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "EV Station Finder",
            },
        )

        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    async def chat_with_mcp(
        self,
        user_message,
        mcp_script_path,
        model="x-ai/grok-4.1-fast",
        vehicle_info=None,
    ):
        """
        Bu fonksiyon:
        1. MCP sunucusunu başlatır.
        2. Araçları (Tools) öğrenir.
        3. LLM'e soruyu ve araçları gönderir.
        4. Gerekirse aracı çalıştırıp cevabı LLM'e geri iletir.
        """

        messages = list(self.history)

        if vehicle_info:
            enhanced_message = f"""
    Kullanıcı isteği: {user_message}
    
    Araç Bilgileri:
    - Marka: {vehicle_info.get("brand", "Bilinmiyor")}
    - Model: {vehicle_info.get("model", "Bilinmiyor")}
    - Batarya: {vehicle_info.get("battery_kwh", 0)} kWh
    - Menzil: {vehicle_info.get("range_km", 0)} km
    """
            messages.append({"role": "user", "content": enhanced_message})
        else:
            messages.append({"role": "user", "content": user_message})

        if ClientSession is None or stdio_client is None:
            raise ImportError("mcp package is required to use chat_with_mcp")

        server_params = StdioServerParameters(
            command="python", args=[mcp_script_path], env=None
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    tools_result = await session.list_tools()

                    openai_tools = [
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema,
                            },
                        }
                        for tool in tools_result.tools
                    ]

                    print("🤖 Model düşünmeye başladı...")
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto",
                    )

                    final_msg = response.choices[0].message

                    if final_msg.tool_calls:
                        messages.append(final_msg)

                        for tool_call in final_msg.tool_calls:
                            fn_name = tool_call.function.name
                            fn_args = json.loads(tool_call.function.arguments)

                            print(f"🛠️  Araç Çağırılıyor: {fn_name} -> {fn_args}")

                            result = await session.call_tool(fn_name, arguments=fn_args)
                            tool_output = result.content[0].text

                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": tool_output,
                                }
                            )

                        print(
                            "✅ Sonuçlar modele iletiliyor, nihai cevap hazırlanıyor..."
                        )
                        final_response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            response_format={"type": "json_object"},
                        )

                        assistant_response = final_response.choices[0].message.content

                        return assistant_response

                    return final_msg.content

        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback

            traceback.print_exc()
            return f"Bir hata oluştu: {str(e)}"

    def reset_history(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("Chat history has been reset.")
