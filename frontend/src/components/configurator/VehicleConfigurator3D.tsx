/**
 * components/configurator/VehicleConfigurator3D.tsx
 * =================================================
 * Composant générique Three.js / React-Three-Fiber pour le rendu 3D temps réel du véhicule.
 * 
 * Générique et agnostique du modèle :
 * - Lit model_registry.ts pour trouver le fichier .glb et material_map.json
 * - Met à jour dynamiquement la couleur de carrosserie sur les matériaux indiqués dans material_map.json
 * - Bascule la visibilité (visible = true/false) des meshes d'accessoires selon les options cochées
 * - Contrôles orbitaux 360° avec contraintes de sol et ombres de contact
 */

import React, { Suspense, useEffect, useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import { getModel3DEntry } from './model_registry';

export interface MaterialMapConfig {
  vehicle_slug?: string;
  carrosserie_materials?: string[];
  glass_materials?: string[];
  rims_materials?: string[];
  wheels_materials?: string[];
  optional_meshes?: Record<string, string[]>;
}

interface ModelRendererProps {
  modelPath: string;
  materialMapPath: string;
  selectedColorHex?: string;
  selectedOptionNames: string[];
  scale?: number;
}

const ModelRenderer: React.FC<ModelRendererProps> = ({
  modelPath,
  materialMapPath,
  selectedColorHex = '#E5E7EB',
  selectedOptionNames,
  scale = 1.0,
}) => {
  const gltf = useGLTF(modelPath);
  const [materialMap, setMaterialMap] = useState<MaterialMapConfig | null>(null);

  // 1. Chargement de la configuration material_map.json associée au modèle
  useEffect(() => {
    let isMounted = true;
    fetch(materialMapPath)
      .then((res) => {
        if (!res.ok) throw new Error(`Impossible de charger ${materialMapPath}`);
        return res.json();
      })
      .then((data: MaterialMapConfig) => {
        if (isMounted) setMaterialMap(data);
      })
      .catch((err) => {
        console.warn('Utilisation du mapping matériel par défaut:', err);
        // Fallback générique
        if (isMounted) {
          setMaterialMap({
            carrosserie_materials: ['Car_Body_Paint', 'Paint', 'Body'],
            glass_materials: ['Car_Glass', 'Windows', 'Glass'],
            rims_materials: ['Rims_Alloy', 'Rims'],
            optional_meshes: {
              'Barres de toit': ['Roof_Bars'],
              'Barres latérales': ['Side_Steps'],
            },
          });
        }
      });

    return () => {
      isMounted = false;
    };
  }, [materialMapPath]);

  // 2. Application de la couleur dynamique et visibilité des accessoires
  useEffect(() => {
    if (!gltf.scene || !materialMap) return;

    const bodyMaterials = new Set(materialMap.carrosserie_materials || ['Car_Body_Paint', 'Paint']);
    const optionalMeshesMap = materialMap.optional_meshes || {};

    // Détermine quels meshes optionnels doivent être visibles
    const activeMeshNames = new Set<string>();
    for (const [optKey, meshList] of Object.entries(optionalMeshesMap)) {
      const isOptionActive = selectedOptionNames.some(
        (name) =>
          name.toLowerCase().includes(optKey.toLowerCase()) ||
          optKey.toLowerCase().includes(name.toLowerCase())
      );
      if (isOptionActive) {
        meshList.forEach((mName) => activeMeshNames.add(mName));
      }
    }

    // Clone & Traverse
    gltf.scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;

        // Gestion de la visibilité des accessoires optionnels
        for (const meshList of Object.values(optionalMeshesMap)) {
          if (meshList.includes(mesh.name)) {
            mesh.visible = activeMeshNames.has(mesh.name);
          }
        }

        // Application des propriétés de matériaux PBR temps réel
        if (mesh.material) {
          const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
          mats.forEach((mat) => {
            const stdMat = mat as THREE.MeshStandardMaterial;
            if (bodyMaterials.has(mat.name) && stdMat.color) {
              stdMat.color.set(selectedColorHex);
              stdMat.metalness = 0.85;
              stdMat.roughness = 0.22;
              stdMat.needsUpdate = true;
            } else if (mat.name === 'Car_Glass') {
              stdMat.transparent = true;
              stdMat.opacity = 0.82;
              stdMat.roughness = 0.05;
              stdMat.metalness = 0.95;
            } else if (mat.name === 'Skid_Silver') {
              stdMat.metalness = 0.88;
              stdMat.roughness = 0.25;
            } else if (mat.name === 'Rims_Alloy') {
              stdMat.metalness = 0.92;
              stdMat.roughness = 0.18;
            } else if (mat.name === 'Headlights_LED') {
              stdMat.emissive = new THREE.Color(0.9, 0.95, 1.0);
              stdMat.emissiveIntensity = 0.6;
            } else if (mat.name === 'Taillights_LED') {
              stdMat.emissive = new THREE.Color(0.8, 0.05, 0.08);
              stdMat.emissiveIntensity = 0.8;
            }
          });
        }
      }
    });
  }, [gltf.scene, materialMap, selectedColorHex, selectedOptionNames]);

  return <primitive object={gltf.scene} scale={scale} position={[0, 0, 0]} />;
};

export interface VehicleConfigurator3DProps {
  vehicleIdOrSlug: string;
  selectedColorHex?: string;
  selectedOptionNames?: string[];
  height?: number | string;
  autoRotate?: boolean;
  onClose?: () => void;
}

export const VehicleConfigurator3D: React.FC<VehicleConfigurator3DProps> = ({
  vehicleIdOrSlug,
  selectedColorHex = '#E5E7EB',
  selectedOptionNames = [],
  height = 480,
  autoRotate = false,
}) => {
  const [hasWebGLError, setHasWebGLError] = useState(false);
  const entry = useMemo(() => getModel3DEntry(vehicleIdOrSlug), [vehicleIdOrSlug]);

  // Si le véhicule n'a pas d'entrée dans model_registry.ts, le composant ne rend rien
  if (!entry) {
    return null;
  }

  if (hasWebGLError) {
    return (
      <div
        style={{
          width: '100%',
          height,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--bg-surface)',
          borderRadius: '16px',
          border: '1px solid var(--border-subtle)',
          color: 'var(--text-muted)',
          padding: 24,
          textAlign: 'center',
        }}
      >
        <span style={{ fontSize: '2.5rem', marginBottom: 12 }}>🚗</span>
        <p style={{ margin: 0, fontWeight: 600, color: 'var(--text-secondary)' }}>
          Rendu 3D non supporté par ce navigateur
        </p>
        <p style={{ margin: '4px 0 0', fontSize: '0.85rem' }}>
          La configuration reste active et modifiable ci-dessous.
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height,
        borderRadius: '16px',
        overflow: 'hidden',
        background: 'radial-gradient(circle at center, #18191d 0%, #08090a 100%)',
        border: '1px solid var(--border-subtle)',
        boxShadow: 'inset 0 0 40px rgba(0,0,0,0.7)',
      }}
    >
      {/* Badge indicateur 3D interactif */}
      <div
        style={{
          position: 'absolute',
          top: 14,
          left: 16,
          zIndex: 10,
          background: 'rgba(15, 23, 42, 0.75)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255,255,255,0.15)',
          padding: '6px 12px',
          borderRadius: '20px',
          fontSize: '0.75rem',
          fontWeight: 700,
          color: 'var(--accent-gold)',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          letterSpacing: '0.04em',
        }}
      >
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', display: 'inline-block' }} />
        VUE 3D TEMPS RÉEL
      </div>

      {/* Guide utilisateur tactile/souris */}
      <div
        style={{
          position: 'absolute',
          bottom: 14,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10,
          background: 'rgba(15, 23, 42, 0.65)',
          backdropFilter: 'blur(6px)',
          padding: '4px 14px',
          borderRadius: '16px',
          fontSize: '0.75rem',
          color: 'rgba(255,255,255,0.7)',
          pointerEvents: 'none',
        }}
      >
        🔄 Glisser pour faire pivoter à 360° • Zoomer avec la molette
      </div>

      <Canvas
        camera={{ position: entry.cameraPosition || [3.8, 1.8, 4.8], fov: 42 }}
        shadows
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping;
          gl.toneMappingExposure = 1.1;
        }}
        onError={() => setHasWebGLError(true)}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.8} />
          <directionalLight position={[6, 10, 6]} intensity={1.6} castShadow />
          <directionalLight position={[-6, 6, -6]} intensity={0.7} />
          <spotLight position={[0, 8, 0]} intensity={0.5} penumbra={1} />

          <ModelRenderer
            modelPath={entry.modelPath}
            materialMapPath={entry.materialMapPath}
            selectedColorHex={selectedColorHex}
            selectedOptionNames={selectedOptionNames}
            scale={entry.scale || 1.0}
          />

          <ContactShadows
            position={[0, 0, 0]}
            opacity={0.75}
            scale={12}
            blur={1.8}
            far={3.0}
            color="#000000"
          />

          <Environment preset="city" />

          <OrbitControls
            enablePan={false}
            minDistance={2.4}
            maxDistance={8.5}
            minPolarAngle={Math.PI / 6}
            maxPolarAngle={Math.PI / 2 - 0.05} // Empêche de passer sous le sol
            autoRotate={autoRotate}
            autoRotateSpeed={0.6}
            dampingFactor={0.05}
          />
        </Suspense>
      </Canvas>
    </div>
  );
};
