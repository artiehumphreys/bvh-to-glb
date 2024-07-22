const canvas = document.getElementById("renderCanvas");
const engine = new BABYLON.Engine(canvas);
const slider = document.getElementById("slider");
const dropdown = document.getElementById("cameraSelect");

let num = 0;
let isPaused = false;
let frame = 0;
let currentFrame = 0;
let maxFrame = 0;
let scene = null;
let camera = null;
let cameraHeads = [];

const createScene = () => {
  const fileName = "Pose3D_BKN_UTA.glb";
  scene = new BABYLON.Scene(engine);
  console.log(`Loading model: ${fileName}`);

  BABYLON.SceneLoader.Append("", fileName, scene, function (scene) {
    cameraHeads = findHeads(scene);
    populateDropdown();
    setCamera(cameraHeads[num]);
    const light = new BABYLON.HemisphericLight(
      "light",
      new BABYLON.Vector3(1, 1, 0),
      scene
    );

    scene.animationGroups.forEach((group) => {
      group.start(true);
    });

    maxFrame = scene.animationGroups[0].to;

    engine.runRenderLoop(() => {
      scene.render();
      updateSlider();
    });
  });

  return scene;
};

function updateSlider() {
  if (
    scene.animationGroups.length > 0 &&
    scene.animationGroups[0].animatables.length > 0
  ) {
    maxFrame = scene.animationGroups[0].to;
    currentFrame = scene.animationGroups[0].animatables[0].masterFrame;
    let sliderVal = (currentFrame / maxFrame) * 100;
    slider.value = sliderVal;
  }
}

function findHeads(scene) {
  let cameras = scene.meshes.filter((node) =>
    node.name.includes("sphere_baseHead")
  );
  cameras.unshift(null);
  return cameras;
}

function populateDropdown() {
  dropdown.innerHTML = "";
  cameraHeads.forEach((head, index) => {
    const option = document.createElement("option");
    option.value = index;
    option.textContent = head ? head.name.split("_")[2] : "Default";
    dropdown.appendChild(option);
  });
}

function setCamera(headNode) {
  if (camera) {
    camera.detachControl(canvas);
  }

  if (headNode === null) {
    camera = new BABYLON.ArcRotateCamera(
      "camera1",
      -Math.PI / 2,
      Math.PI / 2,
      2,
      new BABYLON.Vector3(0, 1, 0),
      scene
    );
    scene.createDefaultCameraOrLight(true, true, true);
  } else {
    camera = new BABYLON.TargetCamera(
      "camera1",
      new BABYLON.Vector3(0, 0, -3),
      scene
    );
    camera.parent = headNode;
    camera.setTarget(headNode.getAbsolutePosition());
  }
  camera.attachControl(canvas, true);
}

function play() {
  scene.animationGroups.forEach((group) => {
    group.play();
  });
}

function pause() {
  scene.animationGroups.forEach((group) => {
    group.pause();
  });
}

window.addEventListener("keydown", function (e) {
  if (e.code === "KeyC") {
    currentFrame = scene.animationGroups[0].animatables[0]?.masterFrame;
    scene = createScene();
  }
  if (e.code === "Space") {
    isPaused = !isPaused;
    isPaused ? pause() : play();
  }
});

dropdown.addEventListener("change", function () {
  num = parseInt(this.value);
  setCamera(cameraHeads[num]);
});

slider.onchange = function () {
  isPaused = false;
  play();
};

slider.oninput = function () {
  isPaused = true;
  pause();
  const maxFrame = scene.animationGroups[0].to;
  frame = Math.floor((this.value / 100) * maxFrame);
  scene.animationGroups.forEach((group) => {
    group.goToFrame(frame);
  });
};

scene = createScene();
