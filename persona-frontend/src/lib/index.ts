// place files you want to import through the `$lib` alias in this folder.

export interface RawInputEvent {
	t: number;
	type: 'm' | 'd' | 'u' | 'kd' | 'ku';
	x?: number;
	y?: number;
	k?: string;
}

export interface DeviceContext {
	sw: number;
	sh: number;
	dpr: number;
	plt: string;
}

export interface BiometricPayload {
	user_id: string;
	session_id: string;
	origin: string;
	is_signup: boolean;
	metadata: DeviceContext;
	events: RawInputEvent[];
}
