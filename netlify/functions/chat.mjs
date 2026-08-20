const SYSTEM_PROMPT = "You are a friendly HR onboarding expert that helps new and current employees. You answer common questions about onboarding steps, company policies, benefits basics, time-off, and where to find internal resources, in clear, welcoming, professional language. Only answer from the policy information the company has provided; if something is unclear, sensitive, or specific to an individual's situation - such as pay, disputes, or personal records - direct them to the HR team or the official HR system rather than guessing. Never invent policies or share personal employee data. Be supportive and concise.";

export default async (request) => {
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ detail: 'Method not allowed' }), { status: 405, headers: { 'Content-Type': 'application/json' } });
  }

  const endpoint = process.env.AZURE_ENDPOINT;
  const deployment = process.env.AZURE_DEPLOYMENT;
  const apiKey = process.env.AZURE_API_KEY;
  if (!endpoint || !deployment || !apiKey || endpoint.includes('<your-resource>') || apiKey === 'paste-your-key') {
    return new Response(JSON.stringify({ detail: 'The HR assistant is not configured yet. Check the server environment settings.' }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }

  try {
    const body = await request.json();
    const messages = Array.isArray(body.messages) ? body.messages : [];
    const azureResponse = await fetch(`${endpoint.replace(/\/$/, '')}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ model: deployment, messages: [{ role: 'system', content: SYSTEM_PROMPT }, ...messages] }),
    });
    if (!azureResponse.ok) throw new Error(`Azure request failed with status ${azureResponse.status}`);
    const result = await azureResponse.json();
    const reply = result.choices?.[0]?.message?.content;
    if (!reply) throw new Error('The model returned an empty response');
    return new Response(JSON.stringify({ reply }), { headers: { 'Content-Type': 'application/json' } });
  } catch (error) {
    console.error('HR assistant request failed:', error.message);
    return new Response(JSON.stringify({ detail: "Sorry, I'm having trouble answering right now. Please try again." }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }
};