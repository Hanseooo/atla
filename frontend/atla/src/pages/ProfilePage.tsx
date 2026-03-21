import { useAuthStore } from "../stores/authStore";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { useState, useEffect } from "react";
import { useChatStore } from "@/stores/chatStore";
import {
  User,
  Mail,
  Camera,
  Moon,
  Sun,
  ShieldCheck,
  LogOut,
  Loader2,
  AlertCircle,
  CheckCircle2,
  AtSign,
  Monitor,
} from "lucide-react";
import { Alert, AlertDescription } from "../components/ui/alert";
import { getErrorMessage } from "../lib/api";

export function ProfilePage() {
  const profile = useAuthStore((state) => state.profile);
  const signOut = useAuthStore((state) => state.signOut);
  const updateProfile = useAuthStore((state) => state.updateProfile);
  const clearChatMessages = useChatStore((state) => state.clearMessages);

  // Form State
  const [email, setEmail] = useState(profile?.email || "");
  const [avatarUrl, setAvatarUrl] = useState(profile?.avatar_url || "");
  const [theme, setTheme] = useState<"light" | "dark" | "system">("system");

  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">(
    "idle"
  );
  const [errorMessage, setErrorMessage] = useState("");

  // track changes to enable/disable save button
  const hasChanges =
    email !== (profile?.email || "") ||
    avatarUrl !== (profile?.avatar_url || "") ||
    theme !== (profile?.preferences?.theme || "system");

  // Sync state if profile loads later
  useEffect(() => {
    if (profile) {
      setEmail(profile.email || "");
      setAvatarUrl(profile.avatar_url || "");
    }
  }, [profile]);

  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus("idle");

    try {
      // Calling backend PATCH /auth/profile
      // Note: Backend currently supports updating email and avatar_url, but not display_name.
      await updateProfile({
        avatar_url: avatarUrl || undefined,
        email: email || undefined,
        preferences: {
          ...profile?.preferences,
          theme,
          last_updated: new Date().toISOString(),
        },
      });
      setSaveStatus("success");
      setTimeout(() => setSaveStatus("idle"), 3000);
    } catch (error: unknown) {
      setSaveStatus("error");
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-0 pb-[80px] md:pb-8 bg-muted/10">
      <div className="max-w-4xl mx-auto mt-4 md:mt-8 space-y-6">
        {/* <div className="flex items-center justify-between px-1"> */}
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between px-1">
          <h1 className="text-3xl font-extrabold tracking-tight">Profile</h1>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              signOut();
              clearChatMessages();
            }}
            className="w-full md:w-auto bg-emerald-600 text-white hover:bg-emerald-700 hover:text-white rounded-full px-6 font-black uppercase tracking-[0.15em] text-[9px] h-10 shadow-lg shadow-emerald-100 transition-all active:scale-95 "
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </Button>
        </div>

        {/* Status Alerts */}
        {saveStatus === "success" && (
          <Alert className="bg-emerald-50 text-emerald-900 border-emerald-200 shadow-sm animate-in fade-in slide-in-from-top-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <AlertDescription className="font-medium">
              Changes saved successfully!
            </AlertDescription>
          </Alert>
        )}

        {saveStatus === "error" && (
          <Alert variant="destructive" className="shadow-sm">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="font-medium">
              {errorMessage}
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 gap-6">
          {/* Section 1: Identity */}
          <Card className="border shadow-sm overflow-hidden py-0 gap-0">
            <CardHeader className="bg-muted/30 border-b py-4 ">
              <CardTitle className="text-lg flex items-center gap-2">
                <User className="h-5 w-5 text-primary" />
                Personal Profile
              </CardTitle>
              <CardDescription>
                How you appear to others in the app
              </CardDescription>
            </CardHeader>
            <CardContent className="py-6 space-y-6">
              {/* Avatar Preview & URL */}
              <div className="flex flex-col sm:flex-row items-center gap-6 pb-6 border-b border-dashed">
                <div className="relative group">
                  <div className="h-24 w-24 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden border-2 border-primary/20 transition-colors group-hover:border-primary/40">
                    {avatarUrl ? (
                      <img
                        src={avatarUrl}
                        alt="Avatar"
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <User className="h-12 w-12 text-primary/40" />
                    )}
                  </div>
                  <div className="absolute -bottom-1 -right-1 bg-background border rounded-full p-1.5 shadow-sm">
                    <Camera className="h-4 w-4 text-muted-foreground" />
                  </div>
                </div>
                <div className="flex-1 w-full space-y-2">
                  <Label htmlFor="avatarUrl">Profile Picture URL</Label>
                  <Input
                    id="avatarUrl"
                    placeholder="https://example.com/photo.jpg"
                    value={avatarUrl}
                    onChange={(e) => setAvatarUrl(e.target.value)}
                    className="h-10"
                  />
                  <p className="text-[11px] text-muted-foreground italic">
                    Paste an image link to update your avatar preview.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Username</Label>
                  <div className="relative">
                    <AtSign className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                    <Input
                      value={profile?.username || ""}
                      disabled
                      className="bg-muted pl-9 font-mono text-sm"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Section 2: Preferences */}
          <Card className="border shadow-sm overflow-hidden py-0 gap-0">
            <CardHeader className="bg-muted/30 border-b py-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <Moon className="h-5 w-5 text-primary" />
                App Preferences
              </CardTitle>
              <CardDescription>
                Customize your application experience
              </CardDescription>
            </CardHeader>
            <CardContent className="py-6 space-y-4">
              <div className="space-y-3">
                <Label>Color Theme</Label>
                <div className="flex p-2 bg-muted rounded-lg w-full md:w-fit">
                  <button
                    onClick={() => setTheme("light")}
                    className={`flex flex-1 md:flex-none justify-center md:justify-start items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${theme === "light" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                  >
                    <Sun className="h-4 w-4" /> <p className="hidden md:flex">Light</p>
                  </button>
                  <button
                    onClick={() => setTheme("dark")}
                    className={`flex flex-1 md:flex-none items-center justify-center md:justify-start gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${theme === "dark" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                  >
                    <Moon className="h-4 w-4" /> <p className="hidden md:flex">Dark</p>
                  </button>
                  <button
                    onClick={() => setTheme("system")}
                    className={`flex flex-1 md:flex-none justify-center md:justify-start items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${theme === "system" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                  >
                    <Monitor className="h-4 w-4" /> <p className="hidden md:flex">System</p>
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Section 3: Security */}
          <Card className="border shadow-sm overflow-hidden py-0 gap-0">
            <CardHeader className="bg-muted/30 border-b py-6">
              <CardTitle className="text-lg flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-primary" />
                Security
              </CardTitle>
              <CardDescription>
                Manage your account security and passwords
              </CardDescription>
            </CardHeader>
            <CardContent className="py-6">
              <Button
                variant="default"
                className="w-full sm:w-auto font-semibold"
              >
                Change Password
              </Button>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex items-center md:justify-end gap-4 px-1">
            <Button
              onClick={handleSave}
              disabled={isSaving || !hasChanges}
              className="flex-1 px-10 font-bold shadow-md shadow-primary/20 transition-all active:scale-95"
            >
              {isSaving ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
