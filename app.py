<!DOCTYPE html>
<html>
<head>
  <title>TakeViva</title>
</head>
<body>

<h2>TakeViva - AI Viva Generator</h2>

<input type="file" id="fileInput">
<button onclick="generate()">Generate Viva Questions</button>

<pre id="output"></pre>

<script>
async function generate() {
    const file = document.getElementById("fileInput").files[0];
    const text = await file.text();

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            model: "gpt-4o-mini",
            messages: [
                { role: "user", content: "Generate 5 viva questions from:\n" + text }
            ]
        })
    });

    const data = await response.json();
    document.getElementById("output").innerText =
        data.choices[0].message.content;
}
</script>

</body>
</html>
