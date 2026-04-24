<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import type { BiometricPayload, RawInputEvent } from '$lib/index';

	let username = $state('');

	let isActive = $state(false);
	let activityProgress = $state(0);
	let anomalyFlags = $state(0);
	let events = $state<RawInputEvent[]>([]);
	let activeTime = $state(0);
	let isTracking = $state(false);
	let canSubmit = $state(true); // Flag to prevent multiple submissions
	let lastEventTimestamp = $state(0);

	const SUBMISSION_INTERVAL = 10000; // 10 seconds
	const TICK_INTERVAL = 100; // 100ms
	const EVENT_THROTTLE_MS = 50; // Capture one event every 50ms max

	let tickTimer: number | undefined;

	function handleMouseDown(event: MouseEvent) {
		isTracking = true;
		addEvent(event);
	}

	function handleMouseMove(event: MouseEvent) {
		if (isTracking) {
			addEvent(event);
		}
	}

	function handleMouseUp() {
		isTracking = false;
	}

	function addEvent(event: MouseEvent) {
		const now = Date.now();
		if (now - lastEventTimestamp < EVENT_THROTTLE_MS) {
			return; // Throttled
		}
		lastEventTimestamp = now;

		if (!isActive) {
			isActive = true; // Mark as active on the first event
		}
		
		// Determine event type: 'm' for mousemove, 'd' for mousedown, 'u' for mouseup
		let eventType: 'm' | 'd' | 'u' = 'm';
		if (event.type === 'mousedown') {
			eventType = 'd';
		} else if (event.type === 'mouseup') {
			eventType = 'u';
		}

		// Normalize coordinates to 0-1 range to match signup format
		const x = event.clientX / window.innerWidth;
		const y = event.clientY / window.innerHeight;

		events.push({
			t: now,
			type: eventType,
			x: parseFloat(x.toFixed(4)),
			y: parseFloat(y.toFixed(4))
		});
	}

	async function submitPayload() {
		if (events.length < 10) {
			// Don't send tiny payloads
			events = [];
			activeTime = 0;
			activityProgress = 0;
			isActive = false;
			return;
		}

		const deviceContext: import('$lib').DeviceContext = {
			sw: window.screen.width,
			sh: window.screen.height,
			dpr: window.devicePixelRatio,
			plt: navigator.platform
		};

		const payload: BiometricPayload = {
			user_id: username,
			session_id: crypto.randomUUID(),
			origin: window.location.origin,
			is_signup: false,
			metadata: deviceContext,
			events: [...events]
		};

		try {
			const response = await fetch('/api/track', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(payload)
			});

			if (response.ok) {
				const result = await response.json();
				if (result === true) {
					anomalyFlags += 1;
				}
				console.log('Anomaly detection result:', result);
			} else {
				console.error('Failed to submit tracking data:', await response.text());
			}
		} catch (error) {
			console.error('Error submitting tracking data:', error);
		} finally {
			// Reset for the next interval
			events = [];
			activeTime = 0;
			activityProgress = 0;
			isActive = false; // Reset active status after submission
			canSubmit = true; // Allow another submission cycle
		}
	}

	if (browser) {
		onMount(() => {
			window.addEventListener('mousedown', handleMouseDown);
			window.addEventListener('mousemove', handleMouseMove);
			window.addEventListener('mouseup', handleMouseUp);
			window.addEventListener('mouseleave', handleMouseUp); // Stop tracking if mouse leaves window

			tickTimer = setInterval(() => {
				// Only count time if we have recent events
				if (events.length > 0) {
					activeTime += TICK_INTERVAL;
					activityProgress = (activeTime / SUBMISSION_INTERVAL) * 100;

					if (activeTime >= SUBMISSION_INTERVAL && canSubmit) {
						canSubmit = false; // Prevent multiple submissions
						submitPayload();
					}
				} else if (activeTime > 0) {
					// If no events are coming in, reset the timer
					activeTime = 0;
					activityProgress = 0;
					isActive = false;
				}
			}, TICK_INTERVAL);

			return () => {
				window.removeEventListener('mousedown', handleMouseDown);
				window.removeEventListener('mousemove', handleMouseMove);
				window.removeEventListener('mouseup', handleMouseUp);
				window.removeEventListener('mouseleave', handleMouseUp);
				clearInterval(tickTimer);
			};
		});
	}
</script>

<input type="text" bind:value={username}>
<div class="container">
	<h1>Secured Page</h1>
	<p>Your activity on this page is being monitored for security purposes.</p>

	<div class="status-card">
		<h2>Monitoring Status</h2>
		<div class="status-item">
			<span>User Status:</span>
			<span class="status-value {isActive ? 'active' : 'idle'}">
				{isActive ? 'Active' : 'Idle'}
			</span>
		</div>
		<div class="status-item">
			<span>Next Submission:</span>
			<div class="progress-bar">
				<div class="progress" style="width: {activityProgress}%"></div>
			</div>
		</div>
		<div class="status-item">
			<span>Anomaly Flags:</span>
			<span class="status-value flags">{anomalyFlags}</span>
		</div>
	</div>
</div>

<style>
	.container {
		max-width: 800px;
		margin: 2rem auto;
		padding: 2rem;
		font-family: sans-serif;
		color: #333;
	}

	h1 {
		color: #1a1a1a;
		text-align: center;
		margin-bottom: 1rem;
	}

	p {
		text-align: center;
		color: #666;
		margin-bottom: 2rem;
	}

	.status-card {
		background-color: #f9f9f9;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	.status-card h2 {
		margin-top: 0;
		margin-bottom: 1.5rem;
		color: #333;
		font-size: 1.25rem;
		border-bottom: 1px solid #eee;
		padding-bottom: 0.75rem;
	}

	.status-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.status-item:last-child {
		margin-bottom: 0;
	}

	.status-item span {
		font-size: 1rem;
	}

	.status-value {
		font-weight: bold;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
	}

	.status-value.active {
		color: #28a745;
		background-color: rgba(40, 167, 69, 0.1);
	}

	.status-value.idle {
		color: #6c757d;
		background-color: rgba(108, 117, 125, 0.1);
	}

    .status-value.flags {
        color: #dc3545;
        background-color: rgba(220, 53, 69, 0.1);
    }

	.progress-bar {
		width: 60%;
		height: 10px;
		background-color: #e9ecef;
		border-radius: 5px;
		overflow: hidden;
	}

	.progress {
		height: 100%;
		background-color: #007bff;
		transition: width 0.1s linear;
	}
</style>

