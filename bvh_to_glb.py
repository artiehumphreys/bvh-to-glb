import bpy  # type: ignore
import sys
import os


def create_sphere_at_bone(bone, armature):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.05, location=armature.matrix_world @ bone.head_local
    )
    sphere = bpy.context.object
    sphere.name = f"Sphere_{bone.name}"

    # Parent the sphere to the bone
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

        armature = bpy.context.object
        print(armature.active_material)
        if armature.type != "ARMATURE":
            continue
        bpy.context.view_layer.objects.active = armature
        armature.data.display_type = "WIRE"
        armature.data.pose_position = "POSE"
        armature.data.show_bone_colors = True

        armature.scale = (10, 10, 10)

        # bpy.ops.object.mode_set(mode="POSE")
        for bone in armature.pose.bones:
            create_sphere_at_bone(bone.bone, armature)

        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="SELECT")

    bpy.ops.export_scene.gltf(filepath=output_name, export_format="GLB")


if __name__ == "__main__":
    convert_bvh_to_glb("output_BVH", "output")
