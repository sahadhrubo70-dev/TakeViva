import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export default async function handler(req, res) {
  try {
    const { text } = req.body;

    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "user",
          content: "এই লেখার উপর ভিত্তি করে 5টি viva প্রশ্ন তৈরি করো:\n" + text
        }
      ]
    });

    const result = completion.choices[0].message.content;

    res.status(200).json({
      questions: result
    });

  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
}
