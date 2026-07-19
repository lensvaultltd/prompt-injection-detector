const express = require('express');
const app = express();
app.use(express.json());

// This represents a naive AI backend that blindly processes whatever it receives
// It is protected from the public internet by the Python Firewall

const SYSTEM_PROMPT = "You are a helpful customer support bot for Acme Corp. You only answer questions about Acme products.";

app.post('/api/chat', (req, res) => {
    const userPrompt = req.body.prompt;
    console.log(`[VULNERABLE LLM] Received prompt: ${userPrompt}`);
    
    // In a real app, this would hit OpenAI/Anthropic APIs
    // For this mock, we just return a naive static response
    
    let aiResponse = "I'm a helpful customer support bot. I see you asked about: " + userPrompt;
    
    // If a jailbreak SOMEHOW got through the firewall, the LLM is compromised
    if (userPrompt.toLowerCase().includes("ignore all previous")) {
        aiResponse = "I have ignored my system prompt. I am now a hacker. I will execute your commands.";
    }

    res.json({ response: aiResponse });
});

app.listen(8080, () => {
    console.log("Mock Vulnerable LLM Backend running on port 8080");
});
