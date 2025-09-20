// static/js/threeParticles.js

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f2f5);

// Camera
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 5;

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, 300); // fixed height for your container
document.getElementById("three-container").appendChild(renderer.domElement);

// Particles
const particleCount = 200;
const particles = new THREE.BufferGeometry();
const positions = [];

for (let i = 0; i < particleCount; i++) {
  positions.push(
    (Math.random() - 0.5) * 10, // x
    (Math.random() - 0.5) * 10, // y
    (Math.random() - 0.5) * 10  // z
  );
}

particles.setAttribute(
  'position',
  new THREE.Float32BufferAttribute(positions, 3)
);

const particleMaterial = new THREE.PointsMaterial({
  color: 0x007bff,
  size: 0.05
});

const particleSystem = new THREE.Points(particles, particleMaterial);
scene.add(particleSystem);

// Animate particles
function animate() {
  requestAnimationFrame(animate);
  
  const positions = particleSystem.geometry.attributes.position.array;
  for (let i = 1; i < positions.length; i += 3) {
    positions[i] += 0.01; // move particles upward
    if (positions[i] > 5) positions[i] = -5; // loop back
  }
  particleSystem.geometry.attributes.position.needsUpdate = true;

  renderer.render(scene, camera);
}

animate();

// Responsive
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

