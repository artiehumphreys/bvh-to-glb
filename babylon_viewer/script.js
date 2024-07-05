const canvas = document.getElementById("renderCanvas");

const engine = new BABYLON.Engine(canvas);

const createScene = () => {
    const fileName = "../output.glb";
    const scene = new BABYLON.Scene(engine);
    const targetFps = 60;

    const camera = new BABYLON.ArcRotateCamera("camera1", -Math.PI / 2, Math.PI / 2, 2, new BABYLON.Vector3(0, 1, 0), scene);
    camera.attachControl(canvas, true);

    BABYLON.SceneLoader.Append("", fileName, scene, function(scene) {
        scene.createDefaultCameraOrLight(true, true, true);
        scene.animationGroups.forEach((group) => {
            group.targetedAnimations.forEach((targetedAnim) => {
                targetedAnim.animation.framePerSecond = targetFps;
            });
            group.start(true);
        });
    });

    return scene;
};

const scene = createScene();

engine.runRenderLoop(() => {
    scene.render();
});