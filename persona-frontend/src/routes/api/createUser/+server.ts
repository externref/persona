import type { BiometricPayload } from '$lib';
import { json } from '@sveltejs/kit';
import { MongoClient } from 'mongodb';

export async function POST({ request}) {
	const { userId, userPasswd, payload }: {userId: string, userPasswd: string, payload: BiometricPayload} = await request.json();
    console.log(payload)
	
	// Store credentials in MongoDB
	const client = new MongoClient('mongodb://localhost:27017');
	try {
		await client.connect();
		const db = client.db('persona');
		const authCollection = db.collection('auth');
		
		await authCollection.insertOne({
			username: userId,
			password: userPasswd,
			createdAt: new Date()
		});
		console.log('User credentials stored in MongoDB');
	} catch (error) {
		console.error('Error storing credentials in MongoDB:', error);
		return json({ status: 500, error: 'Failed to store credentials' });
	} finally {
		await client.close();
	}
	
	await fetch("http://127.0.0.1:8000/api/v0/init",{
        method: "POST",
        body: JSON.stringify(payload)
    })

	return json({ status: 201 });
}