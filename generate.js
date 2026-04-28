import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export default async function handler(req, res) {
  const { text } = req.body;

  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "user",
        content: "এই লেখার উপর ভিত্তি করে ১০টি viva প্রশ্ন তৈরি করো:\n" + text
      }
    ]
  });

  res.status(200).json({
    questions: response.choices[0].message.content
  });
}
