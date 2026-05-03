import React, { useEffect, useState } from "react";
import { Rnd } from "react-rnd";

interface CanvasTryOnProps {
  userImage: string | null;
  necklaceImage: string;
}

export default function CanvasTryOn({
  userImage,
  necklaceImage,
}: CanvasTryOnProps) {
  const [overlayBox, setOverlayBox] = useState({
    x: 120,
    y: 120,
    width: 180,
    height: 180,
  });

  const [transparentNecklace, setTransparentNecklace] = useState("");

  useEffect(() => {
    if (necklaceImage) {
      setTransparentNecklace(necklaceImage);
    }
  }, [necklaceImage]);

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Try-On Area */}
      <div className="relative w-[420px] h-[560px] bg-white rounded-xl overflow-hidden border border-gray-300">
        
        {/* User Image */}
        {userImage && (
          <img
            src={userImage}
            alt="User"
            className="w-full h-full object-cover"
          />
        )}

        {/* Necklace Overlay */}
        {transparentNecklace && (
          <Rnd
            bounds="parent"
            lockAspectRatio={true}
            size={{
              width: overlayBox.width,
              height: overlayBox.height,
            }}
            position={{
              x: overlayBox.x,
              y: overlayBox.y,
            }}
            onDragStop={(e, d) => {
              setOverlayBox((prev) => ({
                ...prev,
                x: d.x,
                y: d.y,
              }));
            }}
            onResizeStop={(e, direction, ref, delta, position) => {
              setOverlayBox({
                width: parseInt(ref.style.width),
                height: parseInt(ref.style.height),
                x: position.x,
                y: position.y,
              });
            }}
            className="border-2 border-dashed border-blue-500"
          >
            <img
              src={transparentNecklace}
              alt="Necklace"
              className="w-full h-full object-contain pointer-events-none"
              draggable={false}
            />
          </Rnd>
        )}
      </div>

      <p className="text-sm text-gray-300 text-center">
        Drag necklace to move • Resize corners to fit your neck
      </p>
    </div>
  );
}