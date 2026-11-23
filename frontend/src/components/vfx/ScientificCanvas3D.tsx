'use client';

import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface ScientificCanvas3DProps {
  className?: string;
  particleCount?: number;
}

export default function ScientificCanvas3D({ className = '', particleCount = 120 }: ScientificCanvas3DProps) {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    // Check reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Dimensions
    const width = mount.clientWidth || 400;
    const height = mount.clientHeight || 400;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 240;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    // Group for entire scientific globe
    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

    // 1. Holographic wireframe sphere
    const sphereGeo = new THREE.IcosahedronGeometry(75, 2);
    const sphereMat = new THREE.MeshBasicMaterial({
      color: 0x19c7d9,
      wireframe: true,
      transparent: true,
      opacity: 0.18,
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
    globeGroup.add(sphereMesh);

    // 2. Inner core glow sphere
    const coreGeo = new THREE.SphereGeometry(30, 16, 16);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0x2878ff,
      wireframe: true,
      transparent: true,
      opacity: 0.25,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    globeGroup.add(coreMesh);

    // 3. Network node particles on sphere surface
    const particleGeo = new THREE.BufferGeometry();
    const particlePos = new Float32Array(particleCount * 3);
    const radius = 78;

    for (let i = 0; i < particleCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;

      particlePos[i * 3] = radius * Math.cos(theta) * Math.sin(phi);
      particlePos[i * 3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
      particlePos[i * 3 + 2] = radius * Math.cos(phi);
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePos, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x19c7d9,
      size: 3.5,
      transparent: true,
      opacity: 0.85,
    });
    const pointsMesh = new THREE.Points(particleGeo, particleMat);
    globeGroup.add(pointsMesh);

    // 4. Orbiting satellite rings
    const ringGeo = new THREE.RingGeometry(95, 96, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x2878ff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35,
    });
    const ringMesh1 = new THREE.Mesh(ringGeo, ringMat);
    ringMesh1.rotation.x = Math.PI / 3;
    globeGroup.add(ringMesh1);

    const ringMesh2 = new THREE.Mesh(ringGeo, ringMat);
    ringMesh2.rotation.y = Math.PI / 4;
    ringMesh2.rotation.x = -Math.PI / 6;
    globeGroup.add(ringMesh2);

    // Mouse parallax tracking
    let mouseX = 0;
    let mouseY = 0;
    const handleMouseMove = (e: MouseEvent) => {
      const rect = mount.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      mouseX = x * 0.4;
      mouseY = y * 0.4;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Resize handler
    const handleResize = () => {
      if (!mount) return;
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    // Animation Loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);

      if (!prefersReducedMotion) {
        globeGroup.rotation.y += 0.003;
        globeGroup.rotation.x += 0.001;
      }

      // Smooth parallax tilt
      globeGroup.rotation.y += (mouseX - globeGroup.rotation.y * 0.1) * 0.05;
      globeGroup.rotation.x += (mouseY - globeGroup.rotation.x * 0.1) * 0.05;

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      if (mount && renderer.domElement) {
        mount.removeChild(renderer.domElement);
      }
      sphereGeo.dispose();
      sphereMat.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      particleGeo.dispose();
      particleMat.dispose();
      ringGeo.dispose();
      ringMat.dispose();
      renderer.dispose();
    };
  }, [particleCount]);

  return <div ref={mountRef} className={`w-full h-full relative ${className}`} />;
}

