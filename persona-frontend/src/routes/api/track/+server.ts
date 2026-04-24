import { json } from '@sveltejs/kit';

export async function POST({ request}) {
	const payload = await request.json();
    
	try {
		// Forward to Python backend for anomaly detection
		const response = await fetch("http://127.0.0.1:8000/api/v0/compare", {
			method: "POST",
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(payload)
		});

		if (!response.ok) {
			console.error('Python backend error:', await response.text());
			return json({ error: 'Failed to compare payload' }, { status: 500 });
		}

		const result = await response.json();
		// Return the anomaly detection result
		return json(result.anomaly);
	} catch (error) {
		console.error('Error forwarding to Python backend:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
}