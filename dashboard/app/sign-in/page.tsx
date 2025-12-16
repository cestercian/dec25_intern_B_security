import { signIn } from "@/auth"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield } from "lucide-react"

export default function SignIn() {
    return (
        <div className="flex h-screen w-full items-center justify-center bg-muted/40 px-4">
            <Card className="w-full max-w-sm">
                <CardHeader className="text-center">
                    <div className="flex justify-center mb-2">
                        <div className="w-12 h-12 rounded-lg bg-primary flex items-center justify-center">
                            <Shield className="h-6 w-6 text-primary-foreground" />
                        </div>
                    </div>
                    <CardTitle className="text-2xl">Welcome Back</CardTitle>
                    <CardDescription>
                        Sign in to your account to access the security dashboard and view your email threat reports.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form
                        action={async () => {
                            "use server"
                            await signIn("google", { redirectTo: "/" })
                        }}
                    >
                        <Button className="w-full" type="submit">
                            Sign in with Google
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
