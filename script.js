/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp32-mpu-6050-web-server/

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.
  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

let scene, camera, renderer, cube;

function parentWidth(elem) {
  return elem.parentElement.clientWidth;
}

function parentHeight(elem) {
  return elem.parentElement.clientHeight;
}

function init3D() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xffffff);

  const element = document.getElementById("3Dcube");

  camera = new THREE.PerspectiveCamera(75, parentWidth(element) / parentHeight(element), 0.1, 1000);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(parentWidth(element), parentHeight(element));

  element.appendChild(renderer.domElement);

  // Create a geometry
  const geometry = new THREE.BoxGeometry(5, 1, 4);

  // Materials of each face
  const cubeMaterials = [
    new THREE.MeshBasicMaterial({ color: 0x03045e }),
    new THREE.MeshBasicMaterial({ color: 0x023e8a }),
    new THREE.MeshBasicMaterial({ color: 0x0077b6 }),
    new THREE.MeshBasicMaterial({ color: 0x03045e }),
    new THREE.MeshBasicMaterial({ color: 0x023e8a }),
    new THREE.MeshBasicMaterial({ color: 0x0077b6 }),
  ];

  const material = new THREE.MeshFaceMaterial(cubeMaterials);

  cube = new THREE.Mesh(geometry, material);
  scene.add(cube);
  camera.position.z = 5;

  animate();
}

// Render loop
function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

// Resize the 3D object when the browser window changes size
function onWindowResize() {
  const element = document.getElementById("3Dcube");
  camera.aspect = parentWidth(element) / parentHeight(element);
  camera.updateProjectionMatrix();
  renderer.setSize(parentWidth(element), parentHeight(element));
}

window.addEventListener('resize', onWindowResize, false);

// Create the 3D representation
init3D();

// Create events for the sensor readings
if (!!window.EventSource) {
  const source = new EventSource('/events');

  source.addEventListener('open', function(e) {
    console.log("Events Connected");
  }, false);

  source.addEventListener('error', function(e) {
    if (e.target.readyState != EventSource.OPEN) {
      console.log("Events Disconnected");
    }
  }, false);

  source.addEventListener('gyro_readings', function(e) {
    const obj = JSON.parse(e.data);
    document.getElementById("gx").innerHTML = obj.gyroX;
    document.getElementById("gy").innerHTML = obj.gyroY;
    document.getElementById("gz").innerHTML = obj.gyroZ;

    // Change cube rotation after receiving the readings
    cube.rotation.x = obj.gyroY;
    cube.rotation.z = obj.gyroX;
    cube.rotation.y = obj.gyroZ;
  }, false);

  source.addEventListener('temperature_reading', function(e) {
    const obj = JSON.parse(e.data);
    document.getElementById("tem").innerHTML = obj.temperature;
  }, false);

  source.addEventListener('humidity_reading', function(e) {
    const obj = JSON.parse(e.data);
    document.getElementById("humidity").innerHTML = obj.humidity;
  }, false);

  source.addEventListener('pressure_reading', function(e) {
    const obj = JSON.parse(e.data);
    document.getElementById("pressure").innerHTML = obj.pressure;
  }, false);

  source.addEventListener('accelerometer_readings', function(e) {
    const obj = JSON.parse(e.data);
    document.getElementById("ax").innerHTML = obj.accX;
    document.getElementById("ay").innerHTML = obj.accY;
    document.getElementById("az").innerHTML = obj.accZ;
  }, false);
}

function resetPosition(element) {
  const xhr = new XMLHttpRequest();
  xhr.open("GET", "/" + element.id, true);
  console.log(element.id);
  xhr.send();
}

setInterval(function() {
  fetch('/data')
    .then(response => response.json())
    .then(data => {
      document.getElementById("ax").innerHTML = data.accX;
      document.getElementById("ay").innerHTML = data.accY;
      document.getElementById("az").innerHTML = data.accZ;
      document.getElementById("tem").innerHTML = data.temperature;
      document.getElementById("humidity").innerHTML = data.humidity;
      document.getElementById("pressure").innerHTML = data.pressure;
    });
}, 5000);