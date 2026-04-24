
<script lang="ts">
	import { type BiometricPayload } from '$lib';

	let payload = $state<BiometricPayload | null>(null);
	let userId = $state('');
	let userPasswd = $state('');
	let showDrawingArea = $state(false);
	let isDrawing = $state(false);
	let canvasElement = $state<HTMLCanvasElement>();
	let drawingCoverage = $state(0);
	let ctx: CanvasRenderingContext2D | null;
	let events: import('$lib').RawInputEvent[] = [];

	$effect(() => {
		if (canvasElement) {
			ctx = canvasElement.getContext('2d');
			// Set canvas resolution based on its display size
			const rect = canvasElement.getBoundingClientRect();
			canvasElement.width = rect.width;
			canvasElement.height = rect.height;
			drawGuideLine();
		}
	});

	function drawGuideLine() {
		if (!ctx || !canvasElement) return;
		ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
		ctx.beginPath();
		ctx.strokeStyle = '#ccc';
		ctx.lineWidth = 2;
		ctx.setLineDash([5, 5]);
		const y = canvasElement.height / 2;
		ctx.moveTo(0, y);
		ctx.lineTo(canvasElement.width, y);
		ctx.stroke();
		ctx.setLineDash([]); // Reset for user drawing
	}

	function handleSignupClick() {
		showDrawingArea = true;
	}

	function recordEvent(e: MouseEvent, type: 'm' | 'd' | 'u') {
		if (!canvasElement) return;
		const rect = canvasElement.getBoundingClientRect();
		const x = (e.clientX - rect.left) / rect.width;
		const y = (e.clientY - rect.top) / rect.height;

		events.push({
			t: Date.now(),
			type: type,
			x: parseFloat(x.toFixed(4)),
			y: parseFloat(y.toFixed(4))
		});
	}

	function handleMouseDown(e: MouseEvent) {
		isDrawing = true;
		drawingCoverage = 0;
		events = []; // Start fresh
		drawGuideLine(); // Clear canvas and redraw guide
		recordEvent(e, 'd');
		if (ctx) {
            
            // @ts-ignore
			const rect = canvasElement.getBoundingClientRect();
			ctx.beginPath();
			ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
			ctx.strokeStyle = '#007bff';
			ctx.lineWidth = 3;
		}
	}

	function handleMouseMove(e: MouseEvent) {
		if (isDrawing && ctx) {
			recordEvent(e, 'm');
            // @ts-ignore
			const rect = canvasElement.getBoundingClientRect();
			ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
			ctx.stroke();
		}
	}

	function handleMouseUp(e: MouseEvent) {
		if (isDrawing) {
			isDrawing = false;
			recordEvent(e, 'u');
			if (ctx) {
				ctx.closePath();
			}
			if (events.length > 1) {
				const xCoordinates = events.map((ev) => ev.x as number);
				const minX = Math.min(...xCoordinates);
				const maxX = Math.max(...xCoordinates);
				drawingCoverage = maxX - minX;
			}
		}
	}
	async function createProfile() {
		if (events.length < 10) {
			alert('Please draw a more substantial line.');
			return;
		}

		if (drawingCoverage < 0.7) {
			alert('Please draw a line that covers at least 70% of the canvas width.');
			return;
		}

		const deviceContext: import('$lib').DeviceContext = {
			sw: window.screen.width,
			sh: window.screen.height,
			dpr: window.devicePixelRatio,
			plt: navigator.platform
		};

		payload = {
			user_id: userId,
			session_id: crypto.randomUUID(),
			origin: window.location.origin,
			is_signup: true,
			metadata: deviceContext,
			events: events
		};

		try {
			const response = await fetch('/api/createUser', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({userId, userPasswd, payload})
			});

			if (response.ok) {
				const result = await response.json();
				alert('Biometric profile created successfully!');
				console.log('Server response:', result);
			} else {
				const errorText = await response.text();
				alert(`Failed to create biometric profile: ${errorText}`);
			}
		} catch (error) {
			console.error('Error sending request:', error);
			alert('An error occurred while creating the profile.');
		}

		showDrawingArea = false; // Hide drawing area, show signup form again
	}
</script>

<main>
	{#if !showDrawingArea}
		<div class="form-container">
			<h1>Create Your Account</h1>
			<p>Start by entering your desired credentials.</p>

			<div class="input-group">
				<label for="userId">User ID</label>
				<input type="text" id="userId" bind:value={userId} placeholder="e.g., user_123" />
			</div>

			<div class="input-group">
				<label for="userPasswd">Password</label>
				<input
					type="password"
					id="userPasswd"
					bind:value={userPasswd}
					placeholder="Choose a secure password"
				/>
			</div>

			<button onclick={handleSignupClick} disabled={!userId || !userPasswd}>Sign Up</button>
		</div>
	{/if}

	{#if showDrawingArea}
		<div class="drawing-container">
			<h2>Biometric Signature</h2>
			<p>Draw a single, straight line from left to right at your normal pace.</p>
			<canvas
				bind:this={canvasElement}
				onmousedown={handleMouseDown}
				onmousemove={handleMouseMove}
				onmouseup={handleMouseUp}
				onmouseleave={handleMouseUp}
			></canvas>
			<button onclick={createProfile} disabled={drawingCoverage < 0.7}>Create Profile</button>
		</div>
	{/if}
</main>

<svelte:head>
	<title>Sign Up</title>
</svelte:head>

<style>
	main {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 2rem;
		gap: 2rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
			'Open Sans', 'Helvetica Neue', sans-serif;
	}

	.form-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 2rem;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		width: 100%;
		max-width: 400px;
		background: #fff;
	}
	.drawing-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 2rem;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		width: 70vw;
		background: #fff;
	}

	h1,
	h2 {
		text-align: center;
		color: #333;
	}

	p {
		text-align: center;
		color: #666;
		margin-bottom: 1rem;
	}

	.input-group {
		display: flex;
		flex-direction: column;
	}

	label {
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #444;
	}

	input {
		padding: 0.75rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 1rem;
	}

	input:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
	}

	button {
		padding: 0.75rem;
		border: none;
		border-radius: 4px;
		background-color: #007bff;
		color: white;
		font-size: 1rem;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	button:hover {
		background-color: #0056b3;
	}

	button:disabled {
		background-color: #ccc;
		cursor: not-allowed;
	}

	canvas {
		border: 1px solid #eee;
		border-radius: 4px;
		cursor: crosshair;
		touch-action: none;
		width: 100%;
		height: 100px; /* Set a fixed height */
		background: #f9f9f9;
	}
</style>
