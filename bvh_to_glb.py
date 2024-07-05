import bpy  # type: ignore
import os


def create_sphere_at_bone(bone, armature):
    bone_length = (bone.tail_local - bone.tail_local).length

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=bone.head)
    sphere = bpy.context.object
    sphere.name = f"Sphere_{bone.name}"
    mod = sphere.modifiers.new(name="Armature", type="ARMATURE")
    mod.object = armature
    sphere.parent = armature
    sphere.parent_type = "BONE"
    sphere.parent_bone = bone.name


def convert_bvh_to_glb(directory, output_name):
    bpy.ops.wm.read_factory_settings(use_empty=True)

    bpy.ops.wm.obj_import(filepath="Basketball_court.obj")

    for filename in os.listdir(directory):
        if not filename.endswith(".bvh"):
            continue
        bvh_path = os.path.join(directory, filename)
        bpy.ops.import_anim.bvh(filepath=bvh_path)
        bpy.context.scene.render.fps = 60

        armature = bpy.context.object
        if armature.type != "ARMATURE":
            continue
        bpy.context.view_layer.objects.active = armature
        armature.data.display_type = "ENVELOPE"
        armature.data.pose_position = "POSE"
        armature.data.show_bone_colors = True

        # bpy.ops.object.mode_set(mode="POSE")
        for bone in armature.pose.bones:
            create_sphere_at_bone(bone.bone, armature)

        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="SELECT")

    bpy.ops.export_scene.gltf(filepath=output_name, export_format="GLB")


if __name__ == "__main__":
    convert_bvh_to_glb("output_BVH", "output")
