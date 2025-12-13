const BACKEND_URL = "http://localhost:8000/api/v1"

export async function fetchEmails(accessToken: string) {
    const response = await fetch(`${BACKEND_URL}/emails/fetch`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ access_token: accessToken }),
    })

    if (!response.ok) {
        throw new Error("Failed to fetch emails")
    }

    return response.json()
}
