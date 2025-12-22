// SDK OLMADAN TEST (Manuel Fetch)
import dotenv from "dotenv";
dotenv.config();

async function rawTest() {
  const apiKey = process.env.AI_GATEWAY_API_KEY;
  console.log("Manuel test yapılıyor...");

  try {
    const response = await fetch(
      "https://gateway.ai.vercel.sh/openai/v1/chat/completions",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages: [{ role: "user", content: "Test mesajı" }],
        }),
      },
    );

    if (!response.ok) {
      throw new Error(
        `Sunucu Hatası: ${response.status} ${response.statusText}`,
      );
    }

    const data = await response.json();
    console.log("\nMANUEL TEST SONUCU:");
    // @ts-ignore
    console.log(data.choices[0].message.content);
  } catch (e) {
    console.error("Manuel test hatası:", e);
  }
}

rawTest();
