"use client";
import { useRef, useEffect } from "react";

export const ThreadsBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Thread animation
    const threads: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      connected: boolean;
    }> = [];

    for (let i = 0; i < 100; i++) {
      threads.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        connected: false,
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update and draw threads
      threads.forEach((thread, i) => {
        thread.x += thread.vx;
        thread.y += thread.vy;

        if (thread.x < 0 || thread.x > canvas.width) thread.vx *= -1;
        if (thread.y < 0 || thread.y > canvas.height) thread.vy *= -1;

        // Draw connections
        threads.forEach((otherThread, j) => {
          if (i < j) {
            const distance = Math.sqrt(
              Math.pow(thread.x - otherThread.x, 2) + Math.pow(thread.y - otherThread.y, 2)
            );
            if (distance < 100) {
              ctx.strokeStyle = `rgba(100, 100, 100, ${0.3 * (1 - distance / 100)})`;
              ctx.lineWidth = 1;
              ctx.beginPath();
              ctx.moveTo(thread.x, thread.y);
              ctx.lineTo(otherThread.x, otherThread.y);
              ctx.stroke();
            }
          }
        });

        // Draw dots
        ctx.fillStyle = "rgba(150, 150, 150, 0.8)";
        ctx.beginPath();
        ctx.arc(thread.x, thread.y, 2, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: "transparent" }}
    />
  );
};
