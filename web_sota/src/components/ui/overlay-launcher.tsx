import { Layout } from "lucide-react";
import { useState } from "react";
import { createRoot } from "react-dom/client";
import { MiniControllerContent } from "@/pages/overlay";

export function OverlayLauncher() {
  const [activePip, setActivePip] = useState<any>(null);

  const handleLaunch = async () => {
    if (activePip) {
      activePip.close();
      setActivePip(null);
      return;
    }

    // Check if Document Picture-in-Picture API is supported
    if ("documentPictureInPicture" in window) {
      try {
        // Request a floating PiP window
        const pipWindow = await (
          window as any
        ).documentPictureInPicture.requestWindow({
          width: 380,
          height: 650,
        });

        // Copy all stylesheet link and style elements to the PiP window head
        const allStyles = Array.from(
          document.querySelectorAll('style, link[rel="stylesheet"]'),
        );
        allStyles.forEach((styleNode) => {
          pipWindow.document.head.appendChild(styleNode.cloneNode(true));
        });

        // Create a div container for mounting the React component
        const container = pipWindow.document.createElement("div");
        container.id = "pip-root";
        container.className =
          "bg-slate-950 text-slate-50 min-h-screen p-4 font-sans";
        pipWindow.document.body.appendChild(container);
        pipWindow.document.body.style.margin = "0";
        pipWindow.document.body.style.backgroundColor = "#020617";

        // Render MiniControllerContent inside the float window
        const root = createRoot(container);
        root.render(
          <MiniControllerContent closeWindow={() => pipWindow.close()} />,
        );

        pipWindow.addEventListener("pagehide", () => {
          setActivePip(null);
        });

        setActivePip(pipWindow);
      } catch (err) {
        console.error("Failed to open Picture-in-Picture window:", err);
        openFallbackPopup();
      }
    } else {
      openFallbackPopup();
    }
  };

  const openFallbackPopup = () => {
    window.open(
      "/overlay",
      "vdj-mcp-overlay",
      "width=380,height=650,menubar=no,status=no,toolbar=no,location=no",
    );
  };

  return (
    <button
      onClick={handleLaunch}
      title="Pop out always-on-top Mini-Controller Overlay"
      className="flex items-center gap-2 rounded-full border border-slate-800 hover:border-slate-700 bg-slate-900 hover:bg-slate-800 px-3 py-1.5 text-xs font-bold text-slate-200 transition-all hover:scale-[1.03] select-none cursor-pointer"
    >
      <Layout className="h-3.5 w-3.5 text-indigo-400" />
      <span>FLOAT OVERLAY</span>
    </button>
  );
}
