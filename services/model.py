import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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
        self.base_url = "https://openrouter.ai/api/v1"  # /chat/completions base_url'de olmamalı, OpenAI client ekler.

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

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
        model="qwen/qwen3-next-80b-a3b-instruct:free",
        vehicle_info=None,
    ):
        """
        Bu fonksiyon:
        1. MCP sunucusunu başlatır.
        2. Araçları (Tools) öğrenir.
        3. LLM'e soruyu ve araçları gönderir.
        4. Gerekirse aracı çalıştırıp cevabı LLM'e geri iletir.
        """

        # Geçmişi kopyala ve yeni mesajı ekle
        # Not: self.history zaten bir liste olduğu için content içine koymak yerine listeye ekliyoruz.
        messages = list(self.history)

        # Araç bilgisi varsa user mesajına ekle

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

        server_params = StdioServerParameters(
            command="python", args=[mcp_script_path], env=None
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Araçları Listele
                    tools_result = await session.list_tools()

                    # OpenAI Formatına Çevir
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

                    # LLM'e İlk İstek
                    print("🤖 Model düşünmeye başladı...")
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto",
                    )

                    final_msg = response.choices[0].message

                    # Tool Kullanımı Kontrolü
                    if final_msg.tool_calls:
                        messages.append(final_msg)  # İlk cevabı geçmişe ekle

                        for tool_call in final_msg.tool_calls:
                            fn_name = tool_call.function.name
                            fn_args = json.loads(tool_call.function.arguments)

                            print(f"🛠️  Araç Çağırılıyor: {fn_name} -> {fn_args}")

                            # MCP Üzerinden Çalıştır
                            result = await session.call_tool(fn_name, arguments=fn_args)
                            tool_output = result.content[0].text

                            # Sonucu Geçmişe Ekle
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": tool_output,
                                }
                            )

                        # Sonuçlarla Tekrar Modele Git
                        print(
                            "✅ Sonuçlar modele iletiliyor, nihai cevap hazırlanıyor..."
                        )
                        final_response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            response_format={"type": "json_object"},
                        )

                        assistant_response = final_response.choices[0].message.content

                        # Cevabı ana geçmişe de kaydetmek isterseniz:
                        # self.history.append({"role": "user", "content": user_message})
                        # self.history.append({"role": "assistant", "content": assistant_response})

                        return assistant_response

                    # Tool kullanılmadıysa
                    return final_msg.content

        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback

            traceback.print_exc()
            return f"Bir hata oluştu: {str(e)}"

    # Modeli temizler ve başlangıç durumuna döner
    def reset_history(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("Chat history has been reset.")
