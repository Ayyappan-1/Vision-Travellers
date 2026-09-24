export type WebAuthnUnavailable = {
  error: 'WEBAUTHN_NOT_CONFIGURED';
  message: string;
};

async function request(path: string, token: string): Promise<never> {
  const response = await fetch(`/api${path}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
  });
  const body = await response.json() as WebAuthnUnavailable;
  throw new Error(body.message || 'WebAuthn is not configured');
}

export const webauthnService = {
  registerCredential: (token: string) => request('/auth/webauthn/register/options', token),
  getAuthenticationOptions: (token: string) => request('/auth/webauthn/authenticate/options', token),
  authenticateWithWebAuthn: (token: string) => request('/auth/webauthn/authenticate/verify', token),
};