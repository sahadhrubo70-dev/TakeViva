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
        role: "system",
        content: "তুমি একজন কঠোর viva examiner।"
      },
      {
        role: "user",
        content: `
এই কনটেন্ট থেকে ৫টা viva প্রশ্ন তৈরি করো এবং প্রতিটির সাথে expected answer দাও:

${text}
        `
      }
    ]
  });

  res.status(200).json({
    data: response.choices[0].message.content
  });
}
